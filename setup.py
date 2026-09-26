#!/usr/bin/env python3
"""Install the documented Claude/Codex environment from original providers."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib

ROOT = Path(__file__).resolve().parent
DEFAULT_COMPONENTS = ('runtime', 'skills', 'agents', 'custom', 'blog', 'gstack', 'integrations', 'context7', 'rules', 'figma', 'hermes')
OPTIONAL_COMPONENTS = ('strix', 'skillui')
COMPONENTS = DEFAULT_COMPONENTS + OPTIONAL_COMPONENTS


def select_components(value):
    """Expand all to the default profile; expensive optional tools stay explicit."""
    requested = [item.strip() for item in value.split(',')]
    unknown = set(requested) - set(COMPONENTS) - {'all'}
    if unknown:
        raise ValueError('Unknown component: ' + ', '.join(sorted(unknown)))
    selected = set(requested)
    if 'all' in selected:
        selected.update(DEFAULT_COMPONENTS)
    return [component for component in COMPONENTS if component in selected]


def command_args(args, *, windows=None, env=None):
    """Resolve native executables; quote batch fallbacks without implicit shell input."""
    args = list(map(str, args))
    windows = os.name == 'nt' if windows is None else windows
    if windows:
        environment = os.environ if env is None else env
        found = shutil.which(args[0], path=environment.get('PATH'))
        if found:
            args[0] = found
        if Path(args[0]).suffix.lower() in ('.cmd', '.bat'):
            # Runtime integrations use node.exe + JS entry points directly. This
            # fallback is for simple terminal shims, not arbitrary shell code.
            if any(any(c in arg for c in ('%', '"', '\r', '\n', '\0')) for arg in args):
                raise ValueError('Unsafe batch argument; use the native executable or Node entry point')
            command = ' '.join('"' + arg + '"' for arg in args)
            # Popen applies CRT escaping to lists, but cmd.exe does not understand
            # its backslash-escaped quotes. Supply cmd's complete command line.
            prefix = subprocess.list2cmdline([environment.get('COMSPEC', 'cmd.exe'),
                                              '/d', '/v:off', '/s', '/c'])
            return prefix + ' "' + command + '"'
    return args


def run(args, **kwargs):
    print('+ ' + ' '.join(map(str, args)), flush=True)
    return subprocess.run(command_args(args, env=kwargs.get('env')), check=True, **kwargs)


def capture(args, **kwargs):
    return subprocess.check_output(command_args(args, env=kwargs.get('env')),
                                   text=True, encoding='utf-8', **kwargs).strip()


def venv_python(root):
    return Path(root) / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def is_link(path):
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


@contextlib.contextmanager
def install_lock(path):
    if is_link(path):
        raise ValueError('Refusing linked installation lock: ' + str(path))
    with path.open('a+b') as lock:
        if os.name == 'nt':
            import msvcrt
            if lock.seek(0, os.SEEK_END) == 0:
                lock.write(b'\0')
                lock.flush()
            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError('Another installation is running for this home') from exc
            try:
                yield
            finally:
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)


def fingerprint(path):
    if getattr(path, 'is_junction', lambda: False)():
        return 'junction:' + str(path.resolve())
    if path.is_symlink():
        return 'link:' + os.readlink(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if path.is_dir():
        entries = [(str(p.relative_to(path)), fingerprint(p))
                   for p in sorted(path.rglob('*')) if (p.is_file() or p.is_symlink())
                   and '__pycache__' not in p.relative_to(path).parts
                   and p.suffix != '.pyc' and p.name != '.DS_Store']
        return hashlib.sha256(json.dumps(entries).encode()).hexdigest()
    return None


def metadata(path):
    import yaml
    text = path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    if not match:
        raise ValueError(f'Missing frontmatter: {path}')
    return yaml.safe_load(match[1]), text[match.end():]


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


class Installer:
    def __init__(self, home, manifest):
        self.windows = os.name == 'nt'
        self.home = home.resolve()
        self.manifest = manifest
        self.state_dir = self.home / '.local/state/ai-setup'
        self.state_file = self.state_dir / 'state.json'
        self.sources = self.home / '.agents/skills/.sources'
        self.bin = self.home / '.local/bin'
        self.state = json.loads(self.state_file.read_text(encoding='utf-8')) if self.state_file.exists() else {
            'files': {}, 'sources': {}, 'completed': []}
        self.env = dict(os.environ)
        # Browser archives can stall on slow links; retain an operator's override.
        self.env.setdefault('PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT', '300000')
        # Child installers use this explicitly selected home, never the operator's configs.
        for key in ('CODEX_HOME', 'CLAUDE_CONFIG_DIR', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME',
                    'XDG_DATA_HOME', 'XDG_STATE_HOME', 'BUN_INSTALL', 'NPM_CONFIG_PREFIX'):
            self.env.pop(key, None)
        self.env.update(HOME=str(self.home), CODEX_HOME=str(self.home / '.codex'),
                        XDG_CONFIG_HOME=str(self.home / '.config'),
                        XDG_CACHE_HOME=str(self.home / '.cache'),
                        XDG_DATA_HOME=str(self.home / '.local/share'),
                        XDG_STATE_HOME=str(self.home / '.local/state'),
                        PLAYWRIGHT_BROWSERS_PATH=str(self.home / '.cache/ms-playwright'),
                        PATH=str(self.bin) + os.pathsep + os.environ.get('PATH', ''),
                        GIT_TERMINAL_PROMPT='0', DISABLE_TELEMETRY='1')
        self.env['PYTHONUTF8'] = '1'
        if self.windows:
            self.env.update(USERPROFILE=str(self.home),
                            APPDATA=str(self.home / 'AppData/Roaming'),
                            LOCALAPPDATA=str(self.home / 'AppData/Local'))
            real_profile = os.environ.get('USERPROFILE')
            if real_profile and self.home == Path(real_profile).resolve():
                for key in ('APPDATA', 'LOCALAPPDATA'):
                    if os.environ.get(key):
                        self.env[key] = os.environ[key]
                browser_cache = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
            else:
                browser_cache = None
            # Match the providers' defaults in fresh terminals; isolate test homes.
            self.env['PLAYWRIGHT_BROWSERS_PATH'] = browser_cache or str(Path(self.env['LOCALAPPDATA']) / 'ms-playwright')

    def safe(self, path):
        path = Path(path)
        if not path.is_relative_to(self.home) or not path.parent.resolve().is_relative_to(self.home):
            raise ValueError(f'Destination escapes selected home: {path}')
        return path

    def save(self):
        self.safe(self.state_file)
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        tmp = self.state_file.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.state, indent=2) + '\n', encoding='utf-8')
        tmp.chmod(0o600)
        tmp.replace(self.state_file)

    def owned(self, path):
        self.safe(path)
        actual = fingerprint(path)
        previous = self.state['files'].get(path.relative_to(self.home).as_posix())
        if actual is not None and actual != previous:
            raise ValueError(f'Preserving unmanaged or locally edited path: {path}')

    def remember(self, path):
        self.state['files'][path.relative_to(self.home).as_posix()] = fingerprint(path)
        self.save()

    def write(self, path, text, mode=None):
        self.safe(path)
        self.owned(path)
        # Match write_text's native newline encoding. Avoid replacing unchanged
        # managed files, which Windows can deny when read-only or held open.
        if path.is_file() and path.read_bytes() == text.replace('\n', os.linesep).encode('utf-8'):
            if mode:
                path.chmod(mode)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + '.ai-setup-tmp')
        temporary.write_text(text, encoding='utf-8')
        if mode:
            temporary.chmod(mode)
        temporary.replace(path)
        self.remember(path)

    def link(self, target, source):
        self.safe(target)
        if is_link(target) and target.resolve() == source.resolve():
            self.remember(target)
            return
        self.owned(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if is_link(target):
            if getattr(target, 'is_junction', lambda: False)():
                target.rmdir()
            else:
                target.unlink()
        if self.windows:
            if source.is_dir():
                # Junctions need neither elevation nor Windows Developer Mode.
                import _winapi
                _winapi.CreateJunction(str(source.resolve()), str(target))
            else:
                shutil.copy2(source, target)
        else:
            target.symlink_to(source)
        self.remember(target)

    def copy_tree(self, source, target, transform=None):
        self.owned(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Materialize only links that remain inside the provider checkout.
        for p in source.rglob('*'):
            if p.is_symlink() and not p.resolve().is_relative_to(source.resolve().parents[1]):
                raise ValueError(f'Provider link escapes source: {p}')
        with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
            staged = Path(tmp) / 'payload'
            shutil.copytree(source, staged, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.DS_Store'))
            if transform:
                transform(staged)
            if target.exists():
                backup = self.state_dir / 'backups' / str(time.time_ns()) / target.name
                backup.parent.mkdir(parents=True, exist_ok=True)
                target.rename(backup)
            staged.rename(target)
        self.remember(target)

    def merge_text(self, path, body, marker='rules'):
        self.safe(path)
        if is_link(path):
            raise ValueError(f'Refusing config symlink: {path}')
        old = path.read_text(encoding='utf-8') if path.exists() else ''
        start, end = f'<!-- ai-setup:{marker}:start -->', f'<!-- ai-setup:{marker}:end -->'
        block = start + '\n' + body.rstrip() + '\n' + end
        if start in old or end in old:
            if old.count(start) != 1 or old.count(end) != 1 or old.index(end) < old.index(start):
                raise ValueError(f'Malformed managed block: {path}')
            current = old[old.index(start):old.index(end) + len(end)]
            if current != block:
                key = path.relative_to(self.home).as_posix() + ':' + marker
                if current != self.state.get('blocks', {}).get(key):
                    raise ValueError(f'Preserving changed managed block: {path}')
                self.backup(path)
                path.write_text(old.replace(current, block, 1), encoding='utf-8')
                self.state['blocks'][key] = block
                self.save()
            return
        self.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(old.rstrip() + ('\n\n' if old else '') + block + '\n', encoding='utf-8')
        self.state.setdefault('blocks', {})[path.relative_to(self.home).as_posix() + ':' + marker] = block
        self.save()

    def backup(self, path):
        self.safe(path)
        if is_link(path):
            raise ValueError(f'Refusing config symlink: {path}')
        if path.exists():
            dest = self.state_dir / 'backups' / str(time.time_ns()) / path.relative_to(self.home)
            dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copy2(path, dest)
            dest.chmod(0o600)

    def fetch(self, spec):
        revision = spec['revision']
        if not re.fullmatch('[0-9a-f]{40}', revision):
            raise ValueError(f'Expected immutable commit for {spec["id"]}')
        source = self.sources / spec['id']
        self.safe(source)
        if source.exists():
            if not (source / '.git').exists():
                raise ValueError(f'Unmanaged source directory: {source}')
            actual = capture(['git', '-C', source, 'rev-parse', 'HEAD'])
            origin = capture(['git', '-C', source, 'remote', 'get-url', 'origin'])
            if actual != revision or origin != spec['url']:
                raise ValueError(f'Source revision/origin changed: {source}; preserve it before upgrading')
            dirty = capture(['git', '-C', source, 'diff', '--name-only', 'HEAD'])
            if dirty:
                actual_diff = capture(['git', '-C', source, 'diff', 'HEAD'])
                if actual_diff != self.state.get('generated_sources', {}).get(spec['id']):
                    raise ValueError(f'Locally edited source: {source}')
        else:
            source.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=source.parent) as tmp:
                checkout = Path(tmp) / 'checkout'
                run(['git', 'init', '-q', checkout], env=self.env)
                if self.windows:
                    run(['git', '-C', checkout, 'config', 'core.longpaths', 'true'], env=self.env)
                run(['git', '-C', checkout, 'remote', 'add', 'origin', spec['url']], env=self.env)
                if spec.get('sparse'):
                    run(['git', '-C', checkout, 'sparse-checkout', 'init', '--cone'], env=self.env)
                    run(['git', '-C', checkout, 'sparse-checkout', 'set', *spec['sparse']], env=self.env)
                run(['git', '-C', checkout, 'fetch', '-q', '--depth=1', '--filter=blob:none', 'origin', revision], env=self.env)
                run(['git', '-C', checkout, 'checkout', '-q', '--detach', 'FETCH_HEAD'], env=self.env)
                if capture(['git', '-C', checkout, 'rev-parse', 'HEAD']) != revision:
                    raise ValueError('Fetched commit mismatch')
                checkout.rename(source)
        self.state['sources'][spec['id']] = {'url': spec['url'], 'revision': revision}
        self.save()
        return source

    def spec(self, name):
        return next(s for s in self.manifest['sources'] if s['id'] == name)

    def install_skill(self, source, entry, blog=False):
        name = entry['name']
        if not re.fullmatch('[a-z0-9][a-z0-9-]*', name):
            raise ValueError(f'Invalid skill name: {name}')
        folder = (source / entry['path']).resolve()
        if not folder.is_relative_to(source.resolve()):
            raise ValueError('Skill path escapes source')
        meta, _ = metadata(folder / 'SKILL.md')
        if meta['name'] != name:
            raise ValueError(f'Skill name mismatch: {folder}: {meta["name"]} != {name}')
        target = self.home / '.agents/skills' / name
        def adapt(staged):
            for src, dst in entry.get('extra_files', {}).items():
                original = (source / src).resolve()
                destination = (staged / dst).resolve()
                if not original.is_relative_to(source.resolve()) or not destination.is_relative_to(staged.resolve()):
                    raise ValueError('Supporting skill asset escapes its provider or destination')
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, destination)
            if entry.get('link_rewrites'):
                p = staged / 'SKILL.md'
                text = p.read_text(encoding='utf-8')
                for old, new in entry['link_rewrites'].items():
                    if old not in text:
                        raise ValueError(f'Expected provider reference missing in {name}: {old}')
                    text = text.replace(old, new)
                p.write_text(text, encoding='utf-8')
            if blog:
                p = staged / 'SKILL.md'
                text = p.read_text(encoding='utf-8')
                end = text.index('\n---', 3) + 4
                p.write_text(text[:end] + '\n\n' + self.blog_note(source) + text[end:], encoding='utf-8')
                if name == 'blog':
                    shutil.copytree(source / 'data', staged / 'data', dirs_exist_ok=True)
        self.copy_tree(folder, target, adapt)
        self.link(self.home / '.claude/skills' / name, target)

    def skills(self):
        for spec in self.manifest['sources']:
            if spec.get('skills'):
                source = self.fetch(spec)
                for entry in spec['skills']:
                    self.install_skill(source, entry)

    def agent(self, path, note=''):
        import yaml
        meta, body = metadata(path)
        name = meta['name']
        filename = slug(name)
        for other in (self.home / '.codex/agents').glob('*.toml'):
            if other.name != filename + '.toml' and tomllib.loads(other.read_text(encoding='utf-8')).get('name') == name:
                raise ValueError(f'Duplicate existing role name: {name} in {other}')
        role = {'name': name, 'description': str(meta['description']).strip(),
                'developer_instructions': note + body}
        self.write(self.home / '.codex/agents' / (filename + '.toml'),
                   '\n'.join(f'{k} = {json.dumps(v, ensure_ascii=False)}' for k, v in role.items()) + '\n')
        self.write(self.home / '.claude/agents' / (filename + '.md'),
                   '---\n' + yaml.safe_dump({'name': filename, 'description': role['description']}) +
                   '---\n\n' + note + body)

    def agents(self):
        for spec in self.manifest['sources']:
            if spec.get('agents'):
                source = self.fetch(spec)
                for path in spec['agents']:
                    self.agent(source / path)

    def custom(self):
        for path in sorted((ROOT / 'custom/skills').glob('*/SKILL.md')):
            meta, _ = metadata(path)
            self.install_skill(ROOT / 'custom', {'name': meta['name'], 'path': str(path.parent.relative_to(ROOT / 'custom'))})

    def hermes(self):
        from hermes_runtime import install
        install(self)

    def blog_note(self, source):
        return (f'## Portable local adapter\n\nCanonical skills: `{self.home}/.agents/skills`. '
                f'Resolve root scripts/, agents/, data/ against `{source}`; execute Python helpers '
                f'with `{venv_python(source / ".venv")}`. Never use a project script with the same name. '
                'Claude uses /blog-*; Codex uses $blog-*. Map Claude tools to the available host tools. '
                'Preserve host restrictions. User/project rules take precedence over approval prompts '
                'and marketing footers; omit community marketing footers. Paid calls and publishing '
                'need task authorization and credentials. Optional Google/Ads/NotebookLM extras are '
                'not activated by this installation.\n\n')

    def blog(self):
        source = self.fetch(self.spec('claude-blog'))
        if self.windows:
            from windows_runtime import blog_renderer_adapter
            blog_renderer_adapter(self, source)
        for path in sorted((source / 'skills').glob('*/SKILL.md')):
            meta, _ = metadata(path)
            self.install_skill(source, {'name': meta['name'], 'path': str(path.parent.relative_to(source))}, True)
        for path in sorted((source / 'agents').glob('*.md')):
            self.agent(path, self.blog_note(source))
        python = venv_python(source / '.venv')
        if not python.exists():
            run([sys.executable, '-m', 'venv', source / '.venv'], env=self.env)
        run([python, '-m', 'pip', 'install', str(source) + '[core,presentation]', 'PyYAML==6.0.3'], env=self.env)
        run([python, '-m', 'patchright', 'install', 'chromium'], env=self.env)

    def rules(self):
        dest = self.home / '.local/share/ai-setup/reference'
        for path in (ROOT / 'config').iterdir():
            if path.is_file():
                self.write(dest / path.name, path.read_text(encoding='utf-8').replace('{{REFERENCE}}', str(dest)))
        body = (dest / 'GLOBAL_RULES.md').read_text(encoding='utf-8').replace('{{REFERENCE}}', str(dest))
        self.merge_text(self.home / '.codex/AGENTS.md', body)
        self.merge_text(self.home / '.claude/CLAUDE.md', body)
        workflow = dest / 'WORKFLOW_RULES.md'
        if workflow.exists():
            for path in (self.home / '.codex/AGENTS.md', self.home / '.claude/CLAUDE.md'):
                self.merge_text(path, workflow.read_text(encoding='utf-8'), 'workflow')
        ignore = self.home / '.config/git/ignore'
        # Respect a user's custom global excludes file; leave it untouched and report it.
        current = subprocess.run(['git', 'config', '--global', '--get', 'core.excludesFile'],
                                 env=self.env, text=True, capture_output=True)
        if current.returncode == 0 and current.stdout.strip():
            ignore = Path(os.path.expandvars(current.stdout.strip().replace('~', str(self.home), 1)))
        elif current.returncode not in (0, 1):
            raise ValueError('Cannot read global Git exclusions: ' + current.stderr.strip())
        self.safe(ignore)
        old = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
        block = (dest / 'ai-local.gitignore').read_text(encoding='utf-8').strip()
        if block not in old:
            if '# BEGIN local AI setup' in old:
                raise ValueError(f'Preserving different local AI ignore block: {ignore}')
            self.backup(ignore)
            ignore.parent.mkdir(parents=True, exist_ok=True)
            ignore.write_text(old.rstrip() + '\n\n' + block + '\n', encoding='utf-8')
        if not current.stdout.strip():
            run(['git', 'config', '--global', 'core.excludesFile', ignore], env=self.env)
        if self.windows:
            # install.ps1 manages the invoking Windows user's PATH. Do not write
            # POSIX shell profiles into native Windows user homes.
            return
        # Activate user-level executable discovery in normal login/interactive shells.
        line = 'export PATH="$HOME/.local/bin:$PATH"'
        for filename in ('.profile', '.bashrc', '.zshrc'):
            p = self.home / filename
            self.safe(p)
            old = p.read_text(encoding='utf-8') if p.exists() else ''
            if line not in old:
                self.backup(p)
                p.write_text(old.rstrip() + '\n\n# ai_setup tools\n' + line + '\n', encoding='utf-8')

    def verify(self):
        if not self.state_file.exists():
            raise ValueError('No successful installation state in selected home')
        errors = []
        if 'hermes' in self.state['completed']:
            from hermes_runtime import verify
            verify(self)
        for component in ('context7', 'strix', 'skillui'):
            if component in self.state['completed']:
                import importlib
                importlib.import_module(component + '_runtime').verify(self)
        for name, expected in self.state['files'].items():
            p = self.home / name
            if fingerprint(p) != expected or (is_link(p) and not p.exists()):
                errors.append('Missing or modified: ' + name)
        for key, block in self.state.get('blocks', {}).items():
            p = self.home / key.rsplit(':', 1)[0]
            if not p.exists() or block not in p.read_text(encoding='utf-8'):
                errors.append('Missing/modified instruction block: ' + str(p))
        for p in (self.home / '.codex/agents').glob('*.toml'):
            tomllib.loads(p.read_text(encoding='utf-8'))
        from runtime import merge
        for name, expected in self.state.get('configuration', {}).items():
            p = self.home / name
            if not p.exists():
                errors.append('Missing configuration: ' + name)
                continue
            actual = tomllib.loads(p.read_text(encoding='utf-8')) if p.suffix == '.toml' else json.loads(p.read_text(encoding='utf-8'))
            try:
                if merge(actual, expected) != actual:
                    errors.append('Missing configuration entries: ' + name)
            except ValueError:
                errors.append('Modified configuration entries: ' + name)
        if errors:
            raise ValueError('\n'.join(errors))
        print(f'PASS: {len(self.state["files"])} managed paths and instruction blocks verified.')
        print('Completed components: ' + ', '.join(self.state['completed']))
        print('Account login, Figma OAuth, and private API/MCP credentials are separate from installation.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'install', 'verify'], nargs='?', default='install')
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--manifest', type=Path, default=ROOT / 'manifest.json')
    parser.add_argument('--only', default='all', help='all = default profile; comma-separated components, e.g. all,strix,skillui or context7')
    args = parser.parse_args()
    try:
        selected = select_components(args.only)
    except ValueError as exc:
        parser.error(str(exc))
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    if manifest.get('schema') != 1:
        parser.error('Unsupported manifest schema')
    installer = Installer(args.home, manifest)
    if args.command == 'plan':
        print(f'Home: {installer.home}\nComponents: {", ".join(selected)}')
        print('Optional (explicit selection only): ' + ', '.join(OPTIONAL_COMPONENTS))
        for s in manifest['sources']:
            print(f'{s["id"]}: {s["url"]} @ {s["revision"]}')
        return
    if args.command == 'verify':
        installer.verify()
        return
    if installer.windows and 'hermes' in selected and installer.home != Path(os.environ['USERPROFILE']).resolve():
        parser.error('The full Windows setup includes Hermes and requires the current user home. '
                     'Omit --home, or use --only with a component list excluding hermes for an isolated test.')
    installer.safe(installer.state_dir / 'install.lock')
    installer.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    with install_lock(installer.state_dir / 'install.lock'):
        actions = {}
        if set(selected) & {'runtime', 'gstack', 'integrations', 'figma'}:
            if installer.windows:
                from windows_runtime import runtime, gstack, integrations, figma
            else:
                from runtime import runtime, gstack, integrations, figma
            actions = {'runtime': runtime, 'gstack': gstack, 'integrations': integrations, 'figma': figma}
        for component in ('context7', 'strix', 'skillui'):
            if component in selected:
                import importlib
                actions[component] = importlib.import_module(component + '_runtime').install
        for component in COMPONENTS:
            if component not in selected:
                continue
            print(f'\n== {component} ==', flush=True)
            if component in actions:
                actions[component](installer)
            else:
                getattr(installer, component)()
            if component not in installer.state['completed']:
                installer.state['completed'].append(component)
            installer.save()
        installer.verify()
        if set(DEFAULT_COMPONENTS).issubset(selected):
            run([sys.executable, ROOT / 'smoke.py', '--home', installer.home], env=installer.env)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, StopIteration) as exc:
        print(f'ERROR: {exc}\nInstallation incomplete. Fix the reported cause and rerun; existing work is preserved.', file=sys.stderr)
        sys.exit(1)
