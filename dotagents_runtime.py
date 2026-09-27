"""Stage custom skills with pinned dotagents without giving it client ownership."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess

from setup import capture, is_link, metadata, run


def isolated_environment(i, home, prefix):
    """All provider configuration and caches belong to the staging home."""
    env = dict(i.env)
    for key in ('NODE_OPTIONS', 'NODE_PATH', 'CLAUDE_CONFIG_DIR', 'NPM_CONFIG_USERCONFIG',
                'npm_config_userconfig', 'npm_config_prefix', 'npm_config_cache'):
        env.pop(key, None)
    env.update(HOME=str(home), USERPROFILE=str(home),
               APPDATA=str(home / 'AppData/Roaming'), LOCALAPPDATA=str(home / 'AppData/Local'),
               CODEX_HOME=str(home / '.codex'), CLAUDE_CONFIG_DIR=str(home / '.claude'),
               XDG_CONFIG_HOME=str(home / '.config'), XDG_CACHE_HOME=str(home / '.cache'),
               XDG_DATA_HOME=str(home / '.local/share'), XDG_STATE_HOME=str(home / '.local/state'),
               DOTAGENTS_HOME=str(home / '.agents'), DOTAGENTS_STATE_DIR=str(home / '.cache/dotagents'),
               NPM_CONFIG_CACHE=str(home / '.cache/npm'), NPM_CONFIG_PREFIX=str(prefix),
               NPM_CONFIG_USERCONFIG=str(home / '.npmrc'), CI='1', NO_COLOR='1')
    return env


def node_and_npm(i):
    """Prefer an existing supported Node; bootstrap the pinned runtime if absent."""
    candidate = shutil.which('node', path=i.env.get('PATH'))
    if candidate:
        node = Path(candidate).resolve()
        try:
            supported = int(capture([node, '--version'], env=i.env).lstrip('v').split('.')[0]) >= 20
        except (ValueError, subprocess.CalledProcessError):
            supported = False
        candidates = [node.parent / 'node_modules/npm/bin/npm-cli.js',
                      node.parent.parent / 'lib/node_modules/npm/bin/npm-cli.js']
        npm = next((path for path in candidates if path.is_file()), None)
        if supported and npm:
            return node, npm
    if i.windows:
        from windows_runtime import ensure_node
        root = ensure_node(i, i.manifest['node'])
        return root / 'node.exe', root / 'node_modules/npm/bin/npm-cli.js'
    from runtime import ensure_node
    system = {'Darwin': 'darwin', 'Linux': 'linux'}.get(platform.system())
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64', 'AMD64': 'x64'}.get(platform.machine())
    if not system or not arch:
        raise ValueError('dotagents requires macOS/Linux/Windows on x64 or arm64')
    root = ensure_node(i, i.manifest['node'], system, arch)
    return root / 'bin/node', root / 'lib/node_modules/npm/bin/npm-cli.js'


def skill_files(folder):
    """Inventory publishable bytes; reject links instead of following outside data."""
    result = {}
    for path in sorted(folder.rglob('*')):
        relative = path.relative_to(folder)
        if any(part in ('.git', '__pycache__', '.DS_Store') for part in relative.parts) or path.suffix == '.pyc':
            continue
        if is_link(path):
            raise ValueError(f'Custom skill contains a link: {path}')
        if path.is_file():
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def stage_custom(i, source_root):
    """Return verified canonical skills in an isolated, disposable provider home."""
    source_root = Path(source_root).resolve()
    skills = sorted(source_root.glob('*/SKILL.md'))
    if not skills:
        raise ValueError(f'No custom skills found: {source_root}')
    names = []
    expected = {}
    for entry in skills:
        name = entry.parent.name
        if not re.fullmatch('[a-z0-9][a-z0-9-]*', name) or metadata(entry)[0]['name'] != name:
            raise ValueError(f'Custom skill name does not match directory: {entry}')
        if is_link(entry.parent):
            raise ValueError(f'Custom skill directory is a link: {entry.parent}')
        names.append(name)
        expected[name] = skill_files(entry.parent)
    version = i.manifest['dotagents']['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('dotagents version must be an exact stable version')
    prefix = i.home / '.local/share/ai-setup/dotagents'
    home = prefix / 'staging-home'
    for path in (prefix, home, home / '.agents'):
        i.safe(path)
        if is_link(path):
            raise ValueError(f'Refusing linked dotagents staging directory: {path}')
        path.mkdir(parents=True, exist_ok=True)
    # Staging is disposable, but a redirected cache/config must not turn it into
    # a route to an operator's real client files on a repeat installation.
    for path in home.rglob('*'):
        if is_link(path):
            raise ValueError(f'Refusing linked dotagents staging path: {path}')
    env = isolated_environment(i, home, prefix)
    (home / '.npmrc').write_text('', encoding='utf-8')
    node, npm = node_and_npm(i)
    package = prefix / 'node_modules/@sentry/dotagents'
    library = prefix / 'node_modules/@sentry/dotagents-lib'
    def installed(path):
        meta = path / 'package.json'
        return meta.is_file() and json.loads(meta.read_text(encoding='utf-8')).get('version') == version
    if not installed(package) or not installed(library):
        run([node, npm, 'install', '--prefix', prefix, '--save-exact', '--ignore-scripts',
             '--no-audit', '--no-fund', f'@sentry/dotagents@{version}',
             f'@sentry/dotagents-lib@{version}'], cwd=home, env=env)
    if not installed(package) or not installed(library):
        raise ValueError('dotagents package version does not match manifest')
    cli = package / 'dist/cli/index.js'
    # The provider intentionally confines local sources to its selected scope.
    # These are generated inputs, never the maintained or installed skill trees.
    inputs = home / '.agents/source'
    if is_link(inputs):
        raise ValueError(f'Refusing linked dotagents input directory: {inputs}')
    if inputs.exists():
        shutil.rmtree(inputs)
    inputs.mkdir()
    for name in names:
        shutil.copytree(source_root / name, inputs / name,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.DS_Store'))
    config = ['# Generated by ai_setup; actual client files remain Installer-owned.',
              'version = 1', 'agents = []', '']
    for name in names:
        config.extend(['[[skills]]', 'name = ' + json.dumps(name),
                       'source = ' + json.dumps('path:./source/' + name), ''])
    (home / '.agents/agents.toml').write_text('\n'.join(config), encoding='utf-8')
    run([node, cli, '--global', 'install'], cwd=home, env=env, stdin=subprocess.DEVNULL)
    staged = home / '.agents/skills'
    actual = {path.parent.name for path in staged.glob('*/SKILL.md')}
    if actual != set(names):
        raise ValueError(f'dotagents staged an unexpected skill inventory: {sorted(actual)}')
    for name in names:
        if is_link(staged / name) or skill_files(staged / name) != expected[name]:
            raise ValueError(f'dotagents changed or omitted custom skill files: {name}')
    i.state['dotagents'] = {'version': version, 'skills': names,
                            'staging_home': str(home.relative_to(i.home))}
    i.save()
    return staged
