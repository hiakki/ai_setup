"""Provider runtimes and client-specific integration adapters."""
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import tempfile
import time
import tomllib

from setup import capture, fingerprint, run


def merge(existing, incoming, context='configuration'):
    """Add missing keys/list entries; refuse to reinterpret an operator setting."""
    result = copy.deepcopy(existing)
    for key, value in incoming.items():
        if key not in result:
            result[key] = value
        elif isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = merge(result[key], value, context + '.' + key)
        elif isinstance(value, list) and isinstance(result[key], list):
            for entry in value:
                if entry not in result[key]:
                    result[key].append(entry)
        elif result[key] != value:
            raise ValueError(f'Existing setting conflicts at {context}.{key}; review it before rerunning')
    return result


def merge_config(i, path, incoming):
    i.safe(path)
    i.backup(path)
    if path.suffix == '.toml':
        import tomlkit
        old = tomlkit.parse(path.read_text(encoding='utf-8')) if path.exists() else tomlkit.document()
        content = tomlkit.dumps(merge(old, incoming))
    else:
        old = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        content = json.dumps(merge(old, incoming), indent=2) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    path.chmod(0o600)
    key = path.relative_to(i.home).as_posix()
    previous = i.state.setdefault('configuration', {}).get(key, {})
    i.state['configuration'][key] = merge(previous, incoming)
    i.save()


def download(url, path):
    run(['curl', '--fail', '--location', '--proto', '=https', '--proto-redir', '=https',
         '--retry', '3', '--connect-timeout', '20', '--max-time', '600', '--silent', '--show-error',
         '--output', path, url])


def ensure_node(i, version, system, arch):
    node_root = i.home / '.local/share/ai-setup' / f'node-v{version}-{system}-{arch}'
    i.safe(node_root)
    if not (node_root / 'bin/node').exists():
        node_root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=node_root.parent) as tmp:
            tmp = Path(tmp)
            name = node_root.name + '.tar.gz'
            base = f'https://nodejs.org/dist/v{version}/'
            download(base + name, tmp / name)
            download(base + 'SHASUMS256.txt', tmp / 'checksums')
            entries = [line.split()[0] for line in (tmp / 'checksums').read_text(encoding='utf-8').splitlines()
                       if line.split()[-1] == name]
            if len(entries) != 1 or hashlib.sha256((tmp / name).read_bytes()).hexdigest() != entries[0]:
                raise ValueError('Node archive checksum mismatch')
            # Debian 12's Python 3.11 lacks tarfile's newer extraction-filter API.
            # Extract the checksum-verified official archive using the system tar.
            run(['tar', '-xzf', tmp / name, '-C', tmp], env=i.env)
            (tmp / node_root.name).rename(node_root)
    return node_root


def runtime(i):
    system = {'Darwin': 'darwin', 'Linux': 'linux'}.get(platform.system())
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64', 'AMD64': 'x64'}.get(platform.machine())
    if not system or not arch:
        raise ValueError('Supported: macOS/Linux x64 or arm64. On Windows use install.ps1 (WSL2).')
    version = i.manifest['node']
    node_root = ensure_node(i, version, system, arch)
    for command in ('node', 'npm', 'npx'):
        i.link(i.bin / command, node_root / 'bin' / command)
    actual = capture([i.bin / 'node', '--version'], env=i.env)
    if actual != 'v' + version:
        raise ValueError('Installed Node version does not match manifest')
    prefix = i.home / '.local/share/ai-setup/npm'
    i.safe(prefix)
    packages = [f'{name}@{version}' for name, version in i.manifest['npm'].items() if name != '@nanonets/graft']
    if i.state.get('npm') != i.manifest['npm']:
        run([i.bin / 'npm', 'install', '--global', '--prefix', prefix, *packages], env=i.env)
        i.state['npm'] = i.manifest['npm']
        i.save()
    for path in (prefix / 'bin').iterdir():
        if path.name == 'graft':
            continue
        i.link(i.bin / path.name, path)
    # tree-sitter 0.21.x used by Graft cannot compile against Node 24 on Linux ARM.
    graft_node = ensure_node(i, i.manifest['graft_node'], system, arch)
    graft_prefix = i.home / '.local/share/ai-setup/graft-npm'
    graft_version = i.manifest['npm']['@nanonets/graft']
    graft_env = dict(i.env, PATH=str(graft_node / 'bin') + os.pathsep + i.env['PATH'])
    if i.state.get('graft_runtime') != graft_version:
        run([graft_node / 'bin/node', graft_node / 'lib/node_modules/npm/bin/npm-cli.js', 'install',
             '--global', '--prefix', graft_prefix, '@nanonets/graft@' + graft_version], env=graft_env)
        i.state['graft_runtime'] = graft_version
        i.save()
    i.write(i.bin / 'graft', '#!/bin/sh\nexec ' + shlex.quote(str(graft_node / 'bin/node')) + ' ' +
            shlex.quote(str(graft_prefix / 'lib/node_modules/@nanonets/graft/dist/cli.js')) + ' "$@"\n', 0o755)
    for command in ('codex', 'claude', 'graft', 'skills', 'bun'):
        run([i.bin / command, '--version'], env=i.env)
    binary = i.bin / 'codebase-memory-mcp'
    expected = i.manifest['codebase_memory_version']
    if not binary.exists():
        spec = i.spec('codebase-memory')
        installer = i.home / '.local/share/ai-setup/installers/codebase-memory.sh'
        i.safe(installer)
        installer.parent.mkdir(parents=True, exist_ok=True)
        download('https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/' + spec['revision'] + '/install.sh', installer)
        if hashlib.sha256(installer.read_bytes()).hexdigest() != i.manifest['codebase_memory_installer_sha256']:
            raise ValueError('Codebase Memory installer checksum mismatch')
        env = dict(i.env, CBM_DOWNLOAD_URL=f'https://github.com/DeusData/codebase-memory-mcp/releases/download/v{expected}')
        run(['bash', installer, '--skip-config', '--dir=' + str(i.bin)], env=env)
        i.remember(binary)
    elif binary.relative_to(i.home).as_posix() not in i.state['files']:
        raise ValueError(f'Preserving existing Codebase Memory binary: {binary}')
    if expected not in capture([binary, '--version'], env=i.env):
        raise ValueError('Codebase Memory version mismatch')


def gstack(i):
    source = i.fetch(i.spec('gstack'))
    if 'gstack' in i.state['completed']:
        i.verify()
        gstack_adapter(i, source)
        return
    # The source layout matters: upstream infers its install destination from this path.
    claude = i.home / '.claude/skills/gstack'
    for folder in (i.home / '.claude/skills', i.home / '.codex/skills', i.home / '.agents/skills'):
        for path in folder.glob('gstack*'):
            if path.relative_to(i.home).as_posix() not in i.state['files']:
                raise ValueError(f'Preserving pre-existing gstack installation: {path}')
    i.link(claude, source)
    env = dict(i.env, GSTACK_SKIP_COREUTILS='1', GSTACK_SKIP_GBRAIN_REGEN='1',
               GSTACK_SKIP_FONTS='1', GSTACK_SKIP_ASIDE='1')
    flags = ['--prefix', '--no-team', '--no-plan-tune-hooks', '--no-timeline-stop-hook']
    for host in ('claude', 'codex'):
        run(['bash', claude / 'setup', '--host', host, *flags], cwd=source, env=env,
            stdin=subprocess.DEVNULL)
    run([source / 'bin/gstack-config', 'set', 'auto_upgrade', 'false'], env=env)
    run([source / 'bin/gstack-patch-names', '.agents/skills', 'true'], cwd=source, env=env)
    for path in sorted((i.home / '.codex/skills').glob('gstack-*')):
        if not path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError(f'Unexpected generated gstack path: {path}')
        target = i.home / '.agents/skills' / path.name
        i.link(target, path.resolve())
        path.unlink()
    router = source / '.agents/skills/gstack/SKILL.md'
    i.write(i.home / '.agents/skills/gstack/SKILL.md', router.read_text(encoding='utf-8'))
    # Keep the runtime adapter, but do not expose a second Codex router/skill tree.
    adapter = i.home / '.codex/skills/gstack'
    if adapter.exists():
        i.remember(adapter)
    gstack_adapter(i, source)
    for folder in (i.home / '.claude/skills', i.home / '.codex/skills'):
        for path in folder.glob('gstack*'):
            i.remember(path)
    i.state.setdefault('generated_sources', {})['gstack'] = capture(['git', '-C', source, 'diff', 'HEAD'])
    i.save()


def gstack_adapter(i, source):
    adapter = i.home / '.codex/skills/gstack'
    if not adapter.is_symlink() and not any((adapter / name).exists() for name in ('SKILL.md', 'browse/SKILL.md', 'make-pdf/SKILL.md')):
        return
    i.owned(adapter)
    backup = i.state_dir / ('gstack-runtime-adapter-' + str(time.time_ns()))
    adapter.rename(backup)
    prefix = adapter.relative_to(i.home).as_posix()
    for key in list(i.state['files']):
        if key == prefix or key.startswith(prefix + '/'):
            del i.state['files'][key]
    adapter.mkdir()
    for name in ('bin', 'scripts', 'setup', 'package.json', 'lib', 'ETHOS.md'):
        if (source / name).exists():
            i.link(adapter / name, source / name)
    for name in ('browse', 'design', 'make-pdf'):
        if (source / name / 'dist').exists():
            i.link(adapter / name / 'dist', source / name / 'dist')
    i.remember(adapter)


def integrations(i):
    if 'integrations' not in i.state['completed']:
        stage = i.state_dir / 'provider-integration-home'
        stage.mkdir(parents=True, exist_ok=True)
        for directory in ('.codex', '.claude'):
            (stage / directory).mkdir(exist_ok=True)
        env = dict(i.env, HOME=str(stage), CODEX_HOME=str(stage / '.codex'),
                   XDG_CONFIG_HOME=str(stage / '.config'), XDG_CACHE_HOME=str(stage / '.cache'),
                   XDG_DATA_HOME=str(stage / '.local/share'), XDG_STATE_HOME=str(stage / '.local/state'))
        # Generate provider-owned hooks/skills in an isolated home, then import only our two clients.
        run([i.bin / 'codebase-memory-mcp', 'install', '-y', '--dir=' + str(stage / '.local/bin')], env=env)
        bootstrap = stage / 'graft-bootstrap'
        bootstrap.mkdir(exist_ok=True)
        run(['git', 'init', '-q', bootstrap], env=env)
        run([i.bin / 'graft', 'init', bootstrap, '--agents', 'agents', 'claude'], env=env)
        local_skill = bootstrap / '.claude/skills/graft'
        if local_skill.exists():
            dest = stage / '.claude/skills/graft'
            if not dest.exists():
                shutil.copytree(local_skill, dest)
        for directory in ('.claude', '.codex', '.agents'):
            root = stage / directory
            if not root.exists():
                continue
            for path in sorted(root.rglob('*')):
                if not path.is_file():
                    continue
                rel = path.relative_to(stage)
                if path.name in ('config.toml', 'hooks.json', 'settings.json'):
                    continue
                if any(part in ('logs', 'sessions', '.git') for part in rel.parts):
                    continue
                text = path.read_text(encoding='utf-8').replace(str(stage), str(i.home))
                dest = i.home / rel
                if path.name in ('AGENTS.md', 'CLAUDE.md'):
                    i.merge_text(dest, text, 'provider-instructions')
                else:
                    i.write(dest, text, path.stat().st_mode & 0o777)
        codex_path = stage / '.codex/config.toml'
        codex = tomllib.loads(codex_path.read_text(encoding='utf-8').replace(str(stage), str(i.home))) if codex_path.exists() else {}
        if 'graft' in codex.get('mcp_servers', {}):
            codex['mcp_servers']['graft']['command'] = str(i.bin / 'graft')
        hook_file = stage / '.codex/hooks.json'
        if hook_file.exists():
            hooks = json.loads(hook_file.read_text(encoding='utf-8').replace(str(stage), str(i.home)))
            codex = merge(codex, hooks)
        # One Codex hook representation. Existing hooks.json stays active and must be reviewed.
        if (i.home / '.codex/hooks.json').exists():
            raise ValueError('Existing ~/.codex/hooks.json: consolidate hooks before importing provider hooks')
        merge_config(i, i.home / '.codex/config.toml', codex)
        settings = stage / '.claude/settings.json'
        if settings.exists():
            merge_config(i, i.home / '.claude/settings.json',
                         json.loads(settings.read_text(encoding='utf-8').replace(str(stage), str(i.home))))
    if not i.state.get('cbm_configured'):
        for key, value in [('auto_index', 'false'), ('auto_watch', 'true'), ('ui_enabled', 'true'), ('ui_port', '9749')]:
            run([i.bin / 'codebase-memory-mcp', 'config', 'set', key, value], env=i.env)
        i.state['cbm_configured'] = True
        i.save()
    playwright_root = i.home / '.local/share/ai-setup/npm/lib/node_modules/@playwright/mcp'
    run([i.bin / 'node', playwright_root / 'node_modules/playwright/cli.js', 'install', 'chromium'], env=i.env)
    executable = capture([i.bin / 'node', '-e', "console.log(require('playwright').chromium.executablePath())"], cwd=playwright_root, env=i.env)
    browser_config = i.home / '.config/ai-setup/playwright.json'
    sandbox = os.environ.get('AI_SETUP_BROWSER_NO_SANDBOX') != '1'
    if not sandbox:
        print('AI_SETUP_BROWSER_NO_SANDBOX=1: Playwright Chromium sandbox explicitly disabled.')
    i.write(browser_config, json.dumps({'browser': {'browserName': 'chromium', 'isolated': True,
             'launchOptions': {'executablePath': executable, 'headless': True,
                               'chromiumSandbox': sandbox}}}, indent=2) + '\n')
    codex_servers = {
        'codebase-memory-mcp': {'command': str(i.bin / 'codebase-memory-mcp')},
        'graft': {'command': str(i.bin / 'graft'), 'args': ['mcp']},
        'playwright': {'command': str(i.home / '.local/share/ai-setup/npm/bin/playwright-mcp'),
                       'args': ['--config', str(browser_config)]},
        'figma': {'url': 'https://mcp.figma.com/mcp'},
    }
    for spec in codex_servers.values():
        if 'command' in spec:
            spec['env'] = {'PATH': str(i.bin) + os.pathsep + os.defpath,
                           'PLAYWRIGHT_BROWSERS_PATH': i.env['PLAYWRIGHT_BROWSERS_PATH']}
    merge_config(i, i.home / '.codex/config.toml', {'mcp_servers': codex_servers})
    claude_servers = {name: dict(spec, type='http' if 'url' in spec else 'stdio')
                      for name, spec in codex_servers.items()}
    merge_config(i, i.home / '.claude.json', {'mcpServers': claude_servers})
    trust_generated_hooks(i)


def trust_generated_hooks(i):
    """Trust only the exact provider hooks installed by this manifest, via Codex's own hashes."""
    import contextlib
    from smoke import RPC
    cwd = i.state_dir / 'client-check'
    cwd.mkdir(exist_ok=True)
    path = i.home / '.codex/config.toml'
    planned = i.state.get('configuration', {}).get('.codex/config.toml', {}).get('hooks', {})
    commands = {hook['command'] for entries in planned.values() if isinstance(entries, list)
                for entry in entries for hook in entry.get('hooks', []) if 'command' in hook}
    with contextlib.closing(RPC([str(i.bin / 'codex'), 'app-server', '--listen', 'stdio://'], i.env, cwd, codex=True)) as rpc:
        result = rpc.call('hooks/list', {'cwds': [str(cwd)]})
    state = {}
    for entry in result['data']:
        if entry.get('errors'):
            raise ValueError('Codex reported invalid generated hooks: ' + str(entry['errors']))
        for hook in entry['hooks']:
            if hook['sourcePath'] == str(path) and hook.get('command') in commands:
                state[hook['key']] = {'trusted_hash': hook['currentHash']}
    merge_config(i, path, {'hooks': {'state': state}})


def figma(i):
    if 'figma' in i.state['completed']:
        return
    spec = i.manifest['figma']
    source = i.fetch({'id': 'openai-plugins', 'url': 'https://github.com/' + spec['repository'] + '.git',
                      'revision': spec['revision'], 'sparse': ['plugins/figma']})
    # Codex reserves official catalog names; a portable local registry must use its own name.
    marketplace = i.home / '.local/share/ai-setup/marketplace'
    i.copy_tree(source / 'plugins/figma', marketplace / 'plugins/figma')
    registry = {'name': 'ai-setup-providers', 'plugins': [{'name': 'figma',
                'source': {'source': 'local', 'path': './plugins/figma'},
                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}}]}
    i.write(marketplace / '.agents/plugins/marketplace.json', json.dumps(registry, indent=2) + '\n')
    run([i.bin / 'codex', 'plugin', 'marketplace', 'add', marketplace], env=i.env)
    run([i.bin / 'codex', 'plugin', 'add', 'figma@ai-setup-providers'], env=i.env)
