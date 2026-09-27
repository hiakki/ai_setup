#!/usr/bin/env python3
"""Distribute approved ai_setup revisions without repeating machine bootstrap."""
import argparse
import contextlib
import functools
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
import time
import uuid

DEFAULT_SOURCE = 'https://github.com/hiakki/ai_setup.git'
SHARED = ('skills', 'agents', 'custom', 'rules', 'docs', 'hub')
HELD_LOCKS = {}


def run(args, **kwargs):
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def capture(args):
    return subprocess.check_output(list(map(str, args)), text=True, encoding='utf-8').strip()


def linked(path):
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


def fingerprint(path):
    if getattr(path, 'is_junction', lambda: False)():
        return 'junction:' + str(path.resolve())
    if path.is_symlink():
        return 'link:' + os.readlink(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if path.is_dir():
        entries = [(str(p.relative_to(path)), fingerprint(p)) for p in sorted(path.rglob('*'))
                   if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts
                   and p.suffix != '.pyc' and p.name != '.DS_Store']
        return hashlib.sha256(json.dumps(entries).encode()).hexdigest()
    return None


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temp.chmod(0o600)
    temp.replace(path)


def state_paths(state):
    return set(state.get('files', {})) | set(state.get('configuration', {})) | {
        key.rsplit(':', 1)[0] for key in state.get('blocks', {})}


def safe(home, relative):
    path = home / relative
    if not path.is_relative_to(home) or not path.parent.resolve().is_relative_to(home):
        raise ValueError('Path escapes the selected home: ' + relative)
    return path


@contextlib.contextmanager
def operation_lock(home, allow_inherited=False):
    home = Path(home).resolve()
    if home in HELD_LOCKS:
        yield
        return
    path = safe(home, '.local/state/ai-setup/hub.lock')
    if linked(path):
        raise ValueError('Refusing linked hub lock')
    inherited = os.environ.get('AI_SETUP_HUB_LOCK_TOKEN') if allow_inherited else None
    if inherited and path.exists():
        try:
            owner = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            owner = {}
        if owner.get('token') == inherited and owner.get('home') == str(home):
            HELD_LOCKS[home] = inherited
            try:
                yield
            finally:
                HELD_LOCKS.pop(home, None)
            return
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('a+b') as stream:
        if os.name == 'nt':
            import msvcrt
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b'0')
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            try:
                token = uuid.uuid4().hex
                stream.seek(0)
                stream.truncate()
                stream.write(json.dumps({'home': str(home), 'token': token}).encode())
                stream.flush()
                HELD_LOCKS[home] = token
                yield
            finally:
                HELD_LOCKS.pop(home, None)
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                token = uuid.uuid4().hex
                stream.seek(0)
                stream.truncate()
                stream.write(json.dumps({'home': str(home), 'token': token}).encode())
                stream.flush()
                HELD_LOCKS[home] = token
                yield
            finally:
                HELD_LOCKS.pop(home, None)
                fcntl.flock(stream, fcntl.LOCK_UN)


def serialized(method):
    @functools.wraps(method)
    def call(self, *args, **kwargs):
        with operation_lock(self.home):
            return method(self, *args, **kwargs)
    return call


def backup_entry(path, destination):
    if linked(path):
        return {'kind': 'junction' if getattr(path, 'is_junction', lambda: False)() else 'link',
                'target': str(path.resolve()) if not path.is_symlink() else os.readlink(path)}
    if path.is_dir():
        shutil.copytree(path, destination, symlinks=True)
        return {'kind': 'directory'}
    if path.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        return {'kind': 'file'}
    return {'kind': 'absent'}


class Hub:
    def __init__(self, home):
        self.home = Path(home).resolve()
        self.state_file = self.home / '.local/state/ai-setup/state.json'
        self.root = self.home / '.local/share/ai-setup'
        self.history = self.home / '.local/state/ai-setup/updates'

    def state(self):
        return json.loads(self.state_file.read_text(encoding='utf-8')) if self.state_file.exists() else {}

    def status(self):
        state = self.state()
        print('Home:', self.home)
        print('Shared components:', ', '.join(c for c in SHARED if c in state.get('completed', [])) or 'none')
        print('Installed source:', state.get('hub', {}).get('revision', 'local checkout / not recorded'))
        print('Shared docs:', self.root / 'docs/README.md')
        for relative, expected in state.get('files', {}).items():
            if fingerprint(safe(self.home, relative)) != expected:
                print('LOCAL EDIT:', relative)
        for record in sorted(self.history.glob('*/update.json'), reverse=True)[:3]:
            data = json.loads(record.read_text(encoding='utf-8'))
            print('Update:', record.parent.name, data['status'], data['revision'])

    def checkout(self, source, ref):
        if not ref or ref.startswith('-') or any(c in ref for c in '\r\n\0'):
            raise ValueError('Invalid Git revision')
        releases = self.root / 'releases'
        safe(self.home, str(releases.relative_to(self.home)))
        releases.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=releases) as temporary:
            clone = Path(temporary) / 'checkout'
            run(['git', 'init', '-q', clone])
            run(['git', '-C', clone, 'config', 'core.longpaths', 'true'])
            run(['git', '-C', clone, 'remote', 'add', 'origin', source])
            env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
            run(['git', '-C', clone, 'fetch', '-q', '--depth=1', 'origin', ref], env=env, timeout=180)
            revision = capture(['git', '-C', clone, 'rev-parse', 'FETCH_HEAD^{commit}'])
            run(['git', '-C', clone, 'checkout', '-q', '--detach', revision])
            for filename in ('hub.py', 'setup.py', 'manifest.json'):
                if not (clone / filename).is_file():
                    raise ValueError('Selected revision has no shared hub support. Publish the updated ai_setup first.')
            # Use a fresh immutable checkout even when a previous cache was edited.
            destination = releases / (revision + '-' + str(time.time_ns()))
            clone.rename(destination)
        return destination, revision

    def snapshot_paths(self, state, checkout, selected):
        paths = set()
        manifest = json.loads((checkout / 'manifest.json').read_text(encoding='utf-8'))
        names = set()
        if 'skills' in selected:
            names.update(entry['name'] for spec in manifest['sources'] for entry in spec.get('skills', []))
        if 'custom' in selected:
            names.update(p.parent.name for p in (checkout / 'custom/skills').glob('*/SKILL.md'))
        for name in names:
            if not re.fullmatch('[a-z0-9][a-z0-9-]*', name):
                raise ValueError('Invalid skill in source manifest: ' + name)
            paths.update(('.agents/skills/' + name, '.claude/skills/' + name))
        for relative in state_paths(state):
            if 'agents' in selected and relative.startswith(('.codex/agents/', '.claude/agents/')):
                paths.add(relative)
            if 'rules' in selected and relative.startswith('.local/share/ai-setup/reference/'):
                paths.add(relative)
        if 'docs' in selected:
            paths.add('.local/share/ai-setup/docs')
        if 'hub' in selected:
            paths.update(('.local/share/ai-setup/hub.py', '.local/share/ai-setup/library.py',
                          '.local/bin/ai-setup', '.local/bin/ai-setup.cmd'))
            paths.update(('.local/share/ai-setup/git-hooks', '.local/state/ai-setup/library.json', '.gitconfig'))
            for name in ('AI_READY_PROJECTS.md', 'PROJECT_INSTRUCTIONS_TEMPLATE.md', 'CENTRAL_LIBRARY.md', 'ai-local.gitignore', 'WINDOWS.md'):
                paths.add('.local/share/ai-setup/reference/' + name)
        if set(selected) & {'rules', 'hub'}:
            paths.update(('.codex/AGENTS.md', '.claude/CLAUDE.md'))
        if 'rules' in selected:
            paths.update(('.gitconfig', '.config/git/ignore', '.profile', '.bashrc', '.zshrc'))
        return paths

    @serialized
    def update(self, source, ref, only=None):
        if not self.state_file.exists():
            raise ValueError('Bootstrap this machine with install.sh or install.ps1 first.')
        before = self.state()
        selected = [x.strip() for x in only.split(',')] if only else [
            c for c in SHARED if c in before.get('completed', [])]
        if not selected or set(selected) - set(SHARED):
            raise ValueError('Update selects only shared components: ' + ','.join(SHARED))
        if set(selected) - set(before.get('completed', [])):
            raise ValueError('Bootstrap newly selected components before updating them.')
        checkout, revision = self.checkout(source, ref)
        # Validate the downloaded selection before taking a snapshot or mutating installation.
        run([sys.executable, checkout / 'setup.py', 'plan', '--home', self.home, '--only', ','.join(selected)])
        paths = self.snapshot_paths(before, checkout, selected)
        size = 0
        for relative in paths:
            path = safe(self.home, relative)
            if linked(path):
                continue
            size += sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not linked(p)) if path.is_dir() else path.stat().st_size if path.is_file() else 0
        if shutil.disk_usage(self.home).free < size * 2 + 1024 * 1024:
            raise ValueError('Insufficient free disk space for the shared-content recovery snapshot')
        snapshot = self.history / str(time.time_ns())
        safe(self.home, str(snapshot.relative_to(self.home)))
        snapshot.mkdir(parents=True, mode=0o700)
        entries = {}
        for relative in sorted(paths):
            path = safe(self.home, relative)
            entries[relative] = backup_entry(path, snapshot / 'files' / relative)
            entries[relative]['before'] = fingerprint(path)
        atomic_json(snapshot / 'state.json', before)
        record = {'status': 'running', 'source': source, 'revision': revision,
                  'components': selected, 'entries': entries}
        atomic_json(snapshot / 'update.json', record)
        try:
            environment = dict(os.environ, AI_SETUP_HUB_LOCK_TOKEN=HELD_LOCKS[self.home])
            run([sys.executable, checkout / 'setup.py', 'update', '--home', self.home,
                 '--only', ','.join(selected)], env=environment)
        except (OSError, subprocess.CalledProcessError):
            record['status'] = 'failed'
            raise
        else:
            record['status'] = 'applied'
        finally:
            after = self.state()
            for relative in (state_paths(after) - state_paths(before)) | set(entries):
                entry = entries.setdefault(relative, {'kind': 'absent', 'before': None})
                entry['after'] = fingerprint(safe(self.home, relative))
            record['after_state'] = fingerprint(self.state_file)
            atomic_json(snapshot / 'update.json', record)
            print('Recovery snapshot:', snapshot.name, flush=True)
        after.setdefault('hub', {}).update(source=source, revision=revision, ref=ref)
        atomic_json(self.state_file, after)
        record['after_state'] = fingerprint(self.state_file)
        atomic_json(snapshot / 'update.json', record)
        print('Updated shared content to', revision)

    @serialized
    def rollback(self):
        records = sorted(self.history.glob('*/update.json'), reverse=True)
        if not records:
            raise ValueError('No update snapshot exists')
        record_file = records[0]
        record = json.loads(record_file.read_text(encoding='utf-8'))
        if record['status'] not in ('applied', 'failed'):
            raise ValueError('Latest update is running or already rolled back; inspect its recovery record.')
        changes = {name: entry for name, entry in record['entries'].items()
                   if entry.get('before') != entry.get('after')}
        # Preflight every changed destination before restoring anything.
        if fingerprint(self.state_file) != record.get('after_state'):
            raise ValueError('Installer state changed after this update; reconcile before rollback.')
        for relative, entry in record['entries'].items():
            if fingerprint(safe(self.home, relative)) != entry.get('after'):
                raise ValueError('Preserving edits made after the update: ' + relative)
        prior = json.loads((record_file.parent / 'state.json').read_text(encoding='utf-8'))
        for relative, entry in changes.items():
            path = safe(self.home, relative)
            if path.exists() or linked(path):
                quarantined = record_file.parent / 'replaced' / relative
                quarantined.parent.mkdir(parents=True, exist_ok=True)
                path.rename(quarantined)
            original = record_file.parent / 'files' / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if entry['kind'] == 'directory':
                shutil.copytree(original, path, symlinks=True)
            elif entry['kind'] == 'file':
                shutil.copy2(original, path)
            elif entry['kind'] == 'link':
                path.symlink_to(entry['target'], target_is_directory=True)
            elif entry['kind'] == 'junction':
                import _winapi
                _winapi.CreateJunction(entry['target'], str(path))
        atomic_json(self.state_file, prior)
        record['status'] = 'rolled-back'
        atomic_json(record_file, record)
        print('Restored shared content from update', record_file.parent.name)

    @serialized
    def contribute(self, name, checkout, new_custom=False):
        if not re.fullmatch('[a-z0-9][a-z0-9-]*', name):
            raise ValueError('Invalid skill name')
        state = self.state()
        if name not in state.get('hub', {}).get('custom_skills', []) and not new_custom:
            raise ValueError('Provider skill or unknown provenance. Use --new-custom only for your own new skill.')
        checkout = Path(checkout).resolve()
        if not (checkout / 'manifest.json').is_file() or not (checkout / 'custom/skills').is_dir():
            raise ValueError('Choose an ai_setup source checkout')
        source = self.home / '.agents/skills' / name
        target = checkout / 'custom/skills' / name
        if linked(source) or not (source / 'SKILL.md').is_file() or not source.resolve().is_relative_to(self.home):
            raise ValueError('Installed skill is missing or outside selected home')
        if not target.parent.resolve().is_relative_to(checkout) or linked(target):
            raise ValueError('Contribution destination escapes source checkout')
        baseline = state.get('files', {}).get('.agents/skills/' + name)
        actual = fingerprint(target)
        if actual == fingerprint(source):
            print('Source already matches installed skill:', name)
            return
        if actual is not None and actual != baseline:
            raise ValueError('Source checkout has independent edits; reconcile them before exporting: ' + str(target))
        for p in source.rglob('*'):
            if linked(p) or p.name == '.git' or p.name == '.env' or p.name.startswith('.env.'):
                raise ValueError('Remove private environment files or links before sharing: ' + str(p.relative_to(source)))
        with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
            payload = Path(temporary) / name
            shutil.copytree(source, payload, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
            if target.exists():
                backup = self.history / ('contribution-' + str(time.time_ns())) / name
                backup.parent.mkdir(parents=True, mode=0o700)
                shutil.copytree(target, backup)
                shutil.rmtree(target)
            payload.rename(target)
        print('Exported to', target)
        print('Review the diff and provenance, validate, then commit and push. Nothing was published.')


def docs(i):
    """Install a portable read-only reference bundle once per user, not per project."""
    from setup import ROOT
    with tempfile.TemporaryDirectory() as temporary:
        bundle = Path(temporary) / 'docs'
        bundle.mkdir()
        for directory in ('docs', 'custom', 'config'):
            shutil.copytree(ROOT / directory, bundle / directory,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        for filename in ('README.md', 'manifest.json'):
            shutil.copy2(ROOT / filename, bundle / filename)
        i.copy_tree(bundle, i.home / '.local/share/ai-setup/docs')


def install(i):
    from setup import ROOT, venv_python
    destination = i.home / '.local/share/ai-setup/hub.py'
    i.write(destination, (ROOT / 'hub.py').read_text(encoding='utf-8'))
    i.write(i.home / '.local/share/ai-setup/library.py', (ROOT / 'library.py').read_text(encoding='utf-8'))
    reference = i.home / '.local/share/ai-setup/reference'
    for name in ('AI_READY_PROJECTS.md', 'PROJECT_INSTRUCTIONS_TEMPLATE.md', 'CENTRAL_LIBRARY.md', 'ai-local.gitignore', 'WINDOWS.md'):
        source = ROOT / 'config' / name
        if source.exists():
            i.write(reference / name, source.read_text(encoding='utf-8').replace('{{REFERENCE}}', str(reference)))
    python = venv_python(i.home / '.local/share/ai-setup/venv')
    if not python.exists():
        python = Path(sys.executable)
    if i.windows:
        wrapper = '@echo off\n"' + str(python).replace('%', '%%') + '" "' + str(destination).replace('%', '%%') + '" %*\nexit /b %errorlevel%\n'
        i.write(i.bin / 'ai-setup.cmd', wrapper)
    else:
        i.write(i.bin / 'ai-setup', '#!/bin/sh\nexec ' + shlex.quote(str(python)) + ' ' +
                shlex.quote(str(destination)) + ' "$@"\n', mode=0o755)
    record = i.state.setdefault('hub', {})
    record['custom_skills'] = sorted(p.parent.name for p in (ROOT / 'custom/skills').glob('*/SKILL.md'))
    try:
        revision = capture(['git', '-C', ROOT, 'rev-parse', 'HEAD'])
        dirty = capture(['git', '-C', ROOT, 'status', '--porcelain'])
        record['revision'] = revision + (' (local changes)' if dirty else '')
    except subprocess.CalledProcessError:
        record['revision'] = 'local directory without Git revision'
    record['checkout'] = str(ROOT)
    i.save()
    guidance = '''# Central shared AI setup

Skills, agent definitions and authored documentation belong in the central library.
Before creating or changing any of them, run `ai-setup search "TOPIC"`, read the
relevant results, then run `ai-setup library` to locate the canonical checkout.
Use `ai-setup search "TOPIC" --refresh` when current remote content is required;
it applies a trusted central update. A failed refresh is not permission to claim
freshness or create a project-local substitute. Report the failure and use clearly
labelled local evidence only. Do not commit or push without task authorization.

Do not create project-local SKILL.md files, skill/agent libraries, Markdown notes,
plans or documentation. Update the central entry instead. Shared content belongs in
custom/skills, custom/agents and docs/shared; public project docs in docs/projects.
Private project docs require an explicitly bound PRIVATE central checkout. If none
is configured, ask for that destination before writing; never upload private content
to the public library. Secrets are never library content. Existing project files are
not automatically migrated or deleted. Local client config, generated runtime/graph
data and minimal routing pointers remain local; preserve existing team instructions.
This central-authoring policy supersedes older personal guidance to create local
project-context, handoff, plan or reusable documentation files.

Use `ai-setup check-project --project PATH` before committing. A Git guard can reject
commits, but unrestricted filesystem tools can still create files. Do not claim
search or central-authoring is enforced by a sandbox when only instructions apply.
Read `''' + str(reference / 'CENTRAL_LIBRARY.md') + '''` for enforcement and exceptions.

Use `ai-setup status` to inspect this user's installation. Shared docs
are at `''' + str(i.home / '.local/share/ai-setup/docs') + '''`.
For a reusable skill improvement, edit its canonical source or use
`ai-setup contribute SKILL --checkout PATH_TO_AI_SETUP` to export an installed edit
for review. Exporting does not commit, push or authorize publication. Third-party
skills stay with their original provider. `ai-setup update` pulls and applies a
central revision only when requested; no scheduled updates are installed.
'''
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.merge_text(path, guidance, 'hub')
    import library
    library_hub = Hub(i.home)
    config = library.settings(library_hub)
    if not config.get('checkout') and (ROOT / '.git').exists() and not ROOT.is_relative_to(library_hub.root / 'releases'):
        library.bind(library_hub, ROOT)
    # An explicit operator disable survives reinstall/update.
    if config.get('guard_enabled', True):
        library.install_guard(library_hub)


def main():
    import library
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('status')
    search = commands.add_parser('search', help='Search central checkouts and installed skills, agents and docs')
    search.add_argument('query')
    search.add_argument('--limit', type=int, default=20)
    search.add_argument('--refresh', action='store_true', help='Apply a central update before searching; fail if refresh fails')
    location = commands.add_parser('library', help='Show or bind central authoring checkouts')
    location.add_argument('--checkout', type=Path)
    location.add_argument('--private', action='store_true', help='Declare the bound repository an authorized private library')
    check = commands.add_parser('check-project', help='Reject project-local library files in the staged diff or a CI commit range')
    check.add_argument('--project', type=Path, default=Path.cwd())
    scope = check.add_mutually_exclusive_group()
    scope.add_argument('--base', help='Compare this approved base commit to HEAD for CI')
    scope.add_argument('--audit', action='store_true', help='Audit existing and ignored files too; never migrate automatically')
    guard = commands.add_parser('guard', help='Enable, inspect or remove the global Git commit gate')
    guard.add_argument('action', choices=('install', 'status', 'remove'))
    guard.add_argument('--project', type=Path, default=Path.cwd())
    hook = commands.add_parser('git-hook', help=argparse.SUPPRESS)
    hook.add_argument('event')
    hook.add_argument('arguments', nargs=argparse.REMAINDER)
    update = commands.add_parser('update')
    update.add_argument('--source', default=DEFAULT_SOURCE)
    update.add_argument('--ref', default='main', help='Approved Git branch, tag or commit SHA')
    update.add_argument('--only', help='Shared components; default is the already installed selection')
    commands.add_parser('rollback')
    contribute = commands.add_parser('contribute')
    contribute.add_argument('name')
    contribute.add_argument('--checkout', type=Path, required=True)
    contribute.add_argument('--new-custom', action='store_true', help='Confirm this is your own newly authored custom skill')
    args = parser.parse_args()
    hub = Hub(args.home)
    if args.command == 'status':
        hub.status()
    elif args.command == 'search':
        library.search(hub, args.query, args.limit, args.refresh)
    elif args.command == 'library':
        if args.private and not args.checkout:
            parser.error('--private requires --checkout')
        library.bind(hub, args.checkout, args.private) if args.checkout else library.locations(hub)
    elif args.command == 'check-project':
        library.check(hub, args.project, args.base, args.audit)
    elif args.command == 'guard':
        if args.action == 'install':
            library.install_guard(hub)
        elif args.action == 'remove':
            library.remove_guard(hub)
        else:
            library.guard_status(hub, args.project)
    elif args.command == 'git-hook':
        library.dispatch(hub, args.event, args.arguments)
    else:
        with operation_lock(hub.home):
            if args.command == 'update':
                hub.update(args.source, args.ref, args.only)
            elif args.command == 'rollback':
                hub.rollback()
            else:
                hub.contribute(args.name, args.checkout, args.new_custom)


if __name__ == '__main__':
    sys.modules.setdefault('hub', sys.modules[__name__])
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
