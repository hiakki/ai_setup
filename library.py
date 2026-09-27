"""Central authoring, bounded local search and a portable Git policy gate."""
import json
import hashlib
import errno
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import sys

from hub import atomic_json, capture, linked, operation_lock, safe

TEXT = {'.md', '.mdx', '.rst', '.adoc', '.txt', '.toml'}
SKIP = {'.git', '.sources', 'node_modules', '.venv', 'venv', '.work', '__pycache__',
        '.next', 'dist', 'build', 'vendor', '.cache'}
ROUTERS = {'AGENTS.md', 'AGENTS.override.md', 'CLAUDE.md', 'CLAUDE.local.md'}
HOOKS = ('applypatch-msg pre-applypatch post-applypatch pre-commit pre-merge-commit '
         'prepare-commit-msg commit-msg post-commit pre-rebase post-checkout post-merge '
         'pre-push pre-receive update proc-receive post-receive post-update '
         'reference-transaction push-to-checkout pre-auto-gc post-rewrite sendemail-validate '
         'fsmonitor-watchman p4-changelist p4-prepare-changelist-msg p4-post-changelist '
         'p4-pre-submit post-index-change').split()


def config_path(hub):
    return safe(hub.home, '.local/state/ai-setup/library.json')


def settings(hub):
    path = config_path(hub)
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def git_env(home):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
               XDG_CONFIG_HOME=str(home / '.config'))
    # Only this user's actual global config; do not inherit test/command overrides.
    for key in list(env):
        if key.startswith('GIT_CONFIG_'):
            env.pop(key)
    return env


def git_root(path):
    return Path(capture(['git', '-C', path, 'rev-parse', '--show-toplevel'])).resolve()


def bind(hub, checkout, private=False):
    root = Path(checkout).expanduser().resolve()
    if git_root(root) != root:
        raise ValueError('Choose the root of a central Git checkout')
    if root.is_relative_to(hub.root / 'releases'):
        raise ValueError('Release caches are read-only inputs, not authoring checkouts')
    if not private and not all((root / p).exists() for p in ('manifest.json', 'custom/skills', 'hub.py')):
        raise ValueError('The shared library must be an ai_setup checkout')
    with operation_lock(hub.home):
        data = settings(hub)
        data['private_checkout' if private else 'checkout'] = str(root)
        atomic_json(config_path(hub), data)
    locations(hub)


def locations(hub):
    data = settings(hub)
    for key in ('checkout', 'private_checkout'):
        print(key + ':', data.get(key, 'not configured'))
    print('Shared skills: custom/skills/<name>/SKILL.md')
    print('Shared agent selections: manifest.json; authored roles: custom/agents/<name>.md')
    print('Shared AI learning/docs: docs/shared/<topic>.md (or the existing canonical docs entry)')
    print('Application architecture, decisions and release docs stay in each application repository.')
    print('Private reusable AI material requires the explicitly bound private checkout.')
    print('No publication is automatic. Never put private material in the shared repository.')


def walk(root):
    if not root.is_dir() or linked(root):
        return
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not linked(Path(directory) / d))
        for name in sorted(files):
            path = Path(directory) / name
            if not linked(path):
                yield path


def search(hub, query, limit=20, refresh=False):
    terms = query.casefold().split()
    if not terms or not 1 <= limit <= 100:
        raise ValueError('Provide a nonempty query and a limit between 1 and 100')
    if refresh:
        state = hub.state().get('hub', {})
        hub.update(state.get('source', 'https://github.com/hiakki/ai_setup.git'),
                   state.get('ref', 'main'))
    state = hub.state().get('hub', {})
    print('Installed revision:', state.get('revision', 'unknown'))
    print('Freshness:', 'remote update succeeded' if refresh else 'local content; remote freshness not checked')
    roots = []
    for key in ('checkout', 'private_checkout'):
        if settings(hub).get(key):
            base = Path(settings(hub)[key])
            if not base.is_dir():
                raise ValueError('Bound authoring checkout is missing: ' + str(base))
            roots += [(key, base / name) for name in ('custom', 'docs', 'config')]
    roots += [('installed', hub.root / 'docs'), ('provider-skill', hub.home / '.agents/skills'),
              ('provider-agent', hub.home / '.claude/agents'), ('provider-agent', hub.home / '.codex/agents')]
    hits, seen = [], set()
    for origin, root in roots:
        for path in walk(root):
            if path.name.startswith('.') or path.suffix.casefold() not in TEXT or path.stat().st_size > 2 * 1024 * 1024:
                continue
            body = path.read_text(encoding='utf-8', errors='replace')
            haystack = (str(path) + '\n' + body).casefold()
            if not all(term in haystack for term in terms):
                continue
            # Prefer canonical source over an identical installed reference copy.
            identity = (path.name, body)
            if identity in seen:
                continue
            seen.add(identity)
            lines = body.splitlines()
            number, snippet = next(((n, line.strip()) for n, line in enumerate(lines, 1)
                                    if any(t in line.casefold() for t in terms)), (1, ''))
            score = sum(str(path).casefold().count(t) * 10 + body.casefold().count(t) for t in terms)
            hits.append((-score, str(path), number, origin, snippet[:240]))
    hits.sort()
    for _, path, number, origin, snippet in hits[:limit]:
        print(f'[{origin}] {path}:{number}\n  {snippet}')
    print(f'{len(hits)} matching files; showing {min(limit, len(hits))}.')
    if not hits:
        print('No match in the searched local text files; this is not proof the remote library has no entry.')
    return hits[:limit]


def reason(name):
    path = PurePosixPath(name)
    parts = [p.casefold() for p in path.parts]
    if path.name in ROUTERS or (len(parts) == 1 and parts[0] in {'readme.md', 'license.md', 'license', 'copying', 'notice'}):
        return None
    if path.name.casefold() == 'skill.md':
        return 'skill definition'
    if any(p in ('skills', 'agents') for p in parts[:-1]) and any(
            p in ('.agents', '.claude', '.codex') for p in parts[:-1]):
        return 'client skill/agent definition'
    if any(p in ('.cursor', '.github') for p in parts[:-1]) and any(p in ('agents', 'skills', 'instructions', 'prompts') for p in parts[:-1]):
        return 'agent instruction library'
    return None


def check(hub, project, base=None, audit=False, quiet=False):
    root = git_root(Path(project).resolve())
    central = {Path(v).resolve() for k, v in settings(hub).items() if k in ('checkout', 'private_checkout')}
    if root in central:
        if not quiet:
            print('Central authoring checkout: local library content is allowed.')
        return []
    if audit:
        names = [p.relative_to(root).as_posix() for p in walk(root)]
    else:
        command = ['git', '-C', root, 'diff', '--name-only', '-z', '--diff-filter=ACMRT', '--no-renames']
        if base:
            base = capture(['git', '-C', root, 'rev-parse', '--verify', '--end-of-options', base + '^{commit}'])
        command += [base, 'HEAD'] if base else ['--cached']
        names = subprocess.check_output(list(map(str, command))).decode('utf-8', errors='surrogateescape').split('\0')
    violations = [(name, reason(name)) for name in names if name and reason(name)]
    if violations:
        for name, why in violations:
            print(f'CENTRAL LIBRARY REQUIRED: {name!r} ({why})', file=sys.stderr)
        print('Run ai-setup search "topic", then ai-setup library. Author reusable AI skills/roles centrally; application docs belong in their project.', file=sys.stderr)
        raise ValueError(f'{len(violations)} project-local library file(s) rejected')
    if not quiet:
        print('PASS: no prohibited ' + ('local files' if audit else 'changed files') + '; existing files were not migrated.')
    return violations


def hooks_dir(hub):
    return safe(hub.home, '.local/share/ai-setup/git-hooks')


def install_guard(hub):
    with operation_lock(hub.home):
        env = git_env(hub.home)
        current = subprocess.run(['git', 'config', '--global', '--get', 'core.hooksPath'],
                                 env=env, text=True, capture_output=True)
        if current.returncode not in (0, 1):
            raise ValueError('Cannot read global Git hook configuration')
        data = settings(hub)
        target = hooks_dir(hub)
        previous = current.stdout.strip()
        if previous != target.as_posix():
            if data.get('guard_enabled'):
                raise ValueError('Global hooks changed independently; preserving the operator setting')
            data['previous_hooks_path'] = previous or None
        target.mkdir(parents=True, exist_ok=True)
        if linked(target):
            raise ValueError('Refusing linked managed hooks directory')
        script = hub.root / 'hub.py'
        if not script.is_file():
            raise ValueError('Install the hub before enabling its Git guard')
        payloads = {}
        for hook in HOOKS:
            path = target / hook
            content = '#!/bin/sh\n# ai-setup central library dispatcher\nexec ' + ' '.join(shlex.quote(str(p).replace('\\', '/')) for p in (
                sys.executable, script, '--home', hub.home, 'git-hook', hook)) + ' "$@"\n'
            expected = data.get('hook_hashes', {}).get(hook)
            if linked(path) or (path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != expected):
                raise ValueError('Preserving an unmanaged hook: ' + str(path))
            payloads[hook] = content
        for hook, content in payloads.items():
            path = target / hook
            path.write_text(content, encoding='utf-8', newline='\n')
            path.chmod(0o755)
        data['hook_hashes'] = {name: hashlib.sha256(content.encode()).hexdigest() for name, content in payloads.items()}
        data['guard_enabled'] = True
        atomic_json(config_path(hub), data)
        subprocess.run(['git', 'config', '--global', 'core.hooksPath', target.as_posix()], env=env, check=True)
    print('Global Git guard enabled. Local hooksPath overrides and --no-verify can bypass it; use required CI for team enforcement.')


def remove_guard(hub):
    with operation_lock(hub.home):
        data = settings(hub)
        env = git_env(hub.home)
        current = subprocess.run(['git', 'config', '--global', '--get', 'core.hooksPath'], env=env, text=True, capture_output=True)
        if current.stdout.strip() != hooks_dir(hub).as_posix():
            raise ValueError('Global hooks changed independently; no settings were changed')
        previous = data.get('previous_hooks_path')
        args = ['git', 'config', '--global'] + (['core.hooksPath', previous] if previous else ['--unset', 'core.hooksPath'])
        subprocess.run(args, env=env, check=True)
        data['guard_enabled'] = False
        atomic_json(config_path(hub), data)
    print('Restored previous global Git hook setting; dispatcher files retained.')


def dispatch(hub, event, args):
    if event not in HOOKS:
        raise ValueError('Unknown Git hook')
    previous = settings(hub).get('previous_hooks_path')
    if previous:
        # Relative hooksPath values use the hook's current directory, just as Git does.
        directory = Path(previous.replace('~', str(hub.home), 1)) if previous.startswith('~/') else Path(previous)
    else:
        # reference-transaction can run during git init before rev-parse works.
        git_dir = os.environ.get('GIT_COMMON_DIR') or os.environ.get('GIT_DIR')
        if git_dir:
            common = Path(git_dir)
            if (common / 'commondir').is_file():
                common = common / (common / 'commondir').read_text().strip()
        else:
            common = Path(capture(['git', 'rev-parse', '--git-common-dir']))
        directory = common / 'hooks'
    original = directory / event
    if original.resolve().parent == hooks_dir(hub).resolve():
        raise ValueError('Recursive Git hook configuration')
    if original.is_file() and os.access(original, os.X_OK):
        command = [str(original.resolve()), *args]
        if os.name == 'nt':
            # Use Git's POSIX shell for native Windows hook/shebang semantics.
            # Passing positional arguments avoids interpolation and preserves stdin.
            git = Path(shutil.which('git') or 'git.exe').resolve()
            candidates = (git.parent / 'sh.exe', git.parent.parent / 'bin/sh.exe',
                          git.parent.parent / 'usr/bin/sh.exe')
            shell = next((p for p in candidates if p.is_file()), None)
            if shell is None:
                raise ValueError('Cannot locate Git for Windows shell to preserve the existing hook')
            command = [str(shell), '-c', 'exec "$@"', 'ai-setup-hook',
                       original.resolve().as_posix(), *args]
        # Unlike git hook run, direct execution inherits the original stdin.
        try:
            result = subprocess.run(command)
        except OSError as exc:
            if os.name == 'nt' or exc.errno != errno.ENOEXEC:
                raise
            # Git also accepts executable shell hooks without a shebang.
            result = subprocess.run(['/bin/sh', str(original.resolve()), *args])
        if result.returncode:
            raise SystemExit(result.returncode)
    if event in ('pre-commit', 'pre-merge-commit', 'pre-applypatch'):
        check(hub, Path.cwd(), quiet=True)


def guard_status(hub, project):
    current = subprocess.run(['git', '-C', str(project), 'config', '--get', 'core.hooksPath'], text=True, capture_output=True)
    expected = hooks_dir(hub).as_posix()
    print('Expected global guard:', expected)
    print('Effective project hooksPath:', current.stdout.strip() or 'Git default')
    if current.returncode != 0 or Path(current.stdout.strip()).resolve() != hooks_dir(hub).resolve():
        raise ValueError('This project does not use the central Git guard; configure a chained check or required CI')
    for name, digest in settings(hub).get('hook_hashes', {}).items():
        path = hooks_dir(hub) / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Managed Git hook is missing or edited: ' + str(path))
    print('Active. This is a commit gate, not a filesystem write prohibition.')
