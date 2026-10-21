"""Provider runtimes and client-specific integration adapters."""
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import re
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
    key = path.relative_to(i.home).as_posix()
    previous = i.state.setdefault('configuration', {}).get(key, {})
    merger = (lambda old, new: merge_managed(old, new, previous)) if i.allow_source_updates else merge
    if path.suffix == '.toml':
        import tomlkit
        old = tomlkit.parse(path.read_text(encoding='utf-8')) if path.exists() else tomlkit.document()
        content = tomlkit.dumps(merger(old, incoming))
    else:
        old = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        content = json.dumps(merger(old, incoming), indent=2) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    path.chmod(0o600)
    i.state['configuration'][key] = merge_managed(previous, incoming, previous)
    i.save()


def merge_managed(existing, incoming, previous, context='configuration'):
    """Upgrade unchanged owned settings while preserving independent operator choices."""
    result = copy.deepcopy(existing)
    for key, value in incoming.items():
        if key not in result:
            result[key] = value
        elif isinstance(value, dict) and isinstance(result[key], dict):
            prior = previous.get(key, {})
            result[key] = merge_managed(result[key], value, prior if isinstance(prior, dict) else {}, context + '.' + key)
        elif result[key] == value:
            continue
        elif key in previous and result[key] == previous[key]:
            result[key] = value
        else:
            raise ValueError(f'Preserving operator setting at {context}.{key}; reconcile before syncing')
    return result


def install_codebase_memory(i):
    binary = i.bin / ('codebase-memory-mcp.exe' if i.windows else 'codebase-memory-mcp')
    expected = i.manifest['codebase_memory_version']
    i.owned(binary)
    pattern = r'(?<![\d.])' + re.escape(expected) + r'(?![\d.])'
    if binary.exists() and re.search(pattern, capture([binary, '--version'], env=i.env)):
        return
    spec = i.spec('codebase-memory')
    i.bin.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cbm-install-', dir=i.bin.parent) as directory:
        stage = Path(directory)
        script = stage / ('install.ps1' if i.windows else 'install.sh')
        download('https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/' + spec['revision'] + '/' + script.name, script)
        checksum = 'codebase_memory_windows_installer_sha256' if i.windows else 'codebase_memory_installer_sha256'
        if hashlib.sha256(script.read_bytes()).hexdigest() != i.manifest[checksum]:
            raise ValueError('Codebase Memory installer checksum mismatch')
        env = dict(i.env, CBM_DOWNLOAD_URL=f'https://github.com/DeusData/codebase-memory-mcp/releases/download/v{expected}')
        if i.windows:
            env['CBM_ARCH'] = 'amd64'
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script]
        else:
            command = ['bash', script]
        run([*command, '--skip-config', '--dir=' + str(stage / 'bin')], env=env)
        candidate = stage / 'bin' / binary.name
        if not re.search(pattern, capture([candidate, '--version'], env=i.env)):
            raise ValueError('Codebase Memory candidate version mismatch; previous binary preserved')
        i.backup(binary)
        candidate.replace(binary)
        i.remember(binary)


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
        raise ValueError('Supported: macOS/Linux x64 or arm64. On native Windows use install.ps1; no WSL required.')
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
    install_codebase_memory(i)


def copy_gstack_skill(i, folder, target, source, stage):
    # Provider render folders link shared sections/assets back into the checkout.
    # Validate followed links before materializing them out of the temporary home.
    roots = (source.resolve(), stage.resolve())
    visited = set()
    for directory, dirs, files in os.walk(folder, followlinks=True):
        resolved = Path(directory).resolve()
        if resolved in visited or not any(resolved.is_relative_to(root) for root in roots):
            raise ValueError('Unsafe or cyclic Gstack skill link: ' + str(directory))
        visited.add(resolved)
        for name in dirs + files:
            resolved = (Path(directory) / name).resolve()
            if not any(resolved.is_relative_to(root) for root in roots):
                raise ValueError('Gstack skill link escapes provider: ' + str(Path(directory) / name))
    with tempfile.TemporaryDirectory(dir=stage) as temporary:
        payload = Path(temporary) / 'skill'
        shutil.copytree(folder, payload)
        i.copy_tree(payload, target)


def gstack(i):
    previous = i.state.get('gstack_revision') or i.state.get('sources', {}).get('gstack', {}).get('revision')
    if previous and 'gstack' in i.state['completed'] and not i.state.get('gstack_revision'):
        # Fetch records the new source before generation succeeds. Preserve the
        # legacy installed revision so a failed upgrade remains retryable.
        i.state['gstack_revision'] = previous
        i.save()
    source = i.fetch(i.spec('gstack'))
    revision = i.spec('gstack')['revision']
    for relative in list(i.state['files']):
        if relative.startswith(('.claude/skills/gstack', '.codex/skills/gstack', '.agents/skills/gstack',
                                '.claude/skills/_gstack-command')):
            i.owned(i.home / relative)
    if 'gstack' in i.state['completed'] and previous == revision:
        # Later components may still have old pins during a full sync.
        return
    from windows_runtime import runtime_adapter, gstack_skill_names
    i.state_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gstack-home-', dir=i.state_dir) as temporary:
        stage = Path(temporary)
        claude = stage / '.claude/skills/gstack'
        claude.parent.mkdir(parents=True)
        if i.windows:
            import _winapi
            _winapi.CreateJunction(str(source.resolve()), str(claude))
            from windows_runtime import git_bash
            shell = git_bash(i)
        else:
            claude.symlink_to(source)
            shell = 'bash'
        # The provider heals hooks/settings even with --no-team; isolate all of it.
        env = dict(i.env, HOME=stage.as_posix(), USERPROFILE=str(stage),
                   CODEX_HOME=str(stage / '.codex'), CLAUDE_CONFIG_DIR=str(stage / '.claude'),
                   XDG_CONFIG_HOME=str(stage / '.config'), XDG_DATA_HOME=str(stage / '.local/share'),
                   XDG_CACHE_HOME=str(stage / '.cache'), XDG_STATE_HOME=str(stage / '.local/state'),
                   GSTACK_HOME=str(stage / '.gstack'), GSTACK_USER_RENDER_DIR=str(stage / '.gstack/render/claude'),
                   GSTACK_SKIP_COREUTILS='1', GSTACK_SKIP_GBRAIN_REGEN='1',
                   GSTACK_SKIP_FONTS='1', GSTACK_SKIP_ASIDE='1')
        if not shutil.which('bunx', path=env['PATH']):
            bun = shutil.which('bun', path=env['PATH'])
            if not bun:
                raise ValueError('Gstack needs Bun; install the runtime component first')
            commands = stage / 'bin'
            commands.mkdir()
            shim = commands / 'bunx'
            shim.write_text('#!/usr/bin/env bash\nexec ' + shlex.quote(Path(bun).as_posix()) + ' x "$@"\n', encoding='utf-8')
            shim.chmod(0o755)
            env['PATH'] = str(commands) + os.pathsep + env['PATH']
        config = i.home / '.codex/config.toml'
        model = tomllib.loads(config.read_text(encoding='utf-8')).get('model') if config.exists() else None
        if model:
            (stage / '.codex').mkdir(parents=True, exist_ok=True)
            (stage / '.codex/config.toml').write_text('model = ' + json.dumps(model) + '\n', encoding='utf-8')
        flags = ['--prefix', '--no-team', '--no-plan-tune-hooks', '--no-timeline-stop-hook']
        try:
            for host in ('claude', 'codex'):
                run([shell, (claude / 'setup').as_posix(), '--host', host, *flags],
                    cwd=source, env=env, stdin=subprocess.DEVNULL)
            run([shell, (source / 'bin/gstack-patch-names').as_posix(), '.agents/skills', 'true'],
                cwd=source, env=env)
            i.link(i.home / '.claude/skills/gstack', source)
            for client, target in (('.claude', '.claude'), ('.codex', '.agents')):
                for folder in sorted((stage / client / 'skills').glob('gstack-*')):
                    copy_gstack_skill(i, folder, i.home / target / 'skills' / folder.name, source, stage)
            alias = stage / '.claude/skills/_gstack-command'
            if alias.exists():
                copy_gstack_skill(i, alias, i.home / '.claude/skills/_gstack-command', source, stage)
            i.write(i.home / '.agents/skills/gstack/SKILL.md',
                    (source / '.agents/skills/gstack/SKILL.md').read_text(encoding='utf-8'))
            runtime_adapter(i, source)
            gstack_skill_names(i)
            i.state['gstack_revision'] = revision
        finally:
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
    spec = i.manifest['figma']
    previous = i.state.get('figma_revision') or i.state.get('sources', {}).get('openai-plugins', {}).get('revision')
    if previous and 'figma' in i.state['completed']:
        if not i.state.get('figma_revision'):
            i.state['figma_revision'] = previous
            i.save()
        if previous == spec['revision']:
            return
    source = i.fetch({'id': 'openai-plugins', 'url': 'https://github.com/' + spec['repository'] + '.git',
                      'revision': spec['revision'], 'sparse': ['plugins/figma']})
    # Codex reserves official catalog names; a portable local registry must use its own name.
    marketplace = i.home / '.local/share/ai-setup/marketplace'
    i.copy_tree(source / 'plugins/figma', marketplace / 'plugins/figma')
    registry = {'name': 'ai-setup-providers', 'plugins': [{'name': 'figma',
                'source': {'source': 'local', 'path': './plugins/figma'},
                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}}]}
    i.write(marketplace / '.agents/plugins/marketplace.json', json.dumps(registry, indent=2) + '\n')
    (i.home / '.codex').mkdir(parents=True, exist_ok=True)
    if i.windows:
        from windows_runtime import command
        codex = command(i, 'codex')
    else:
        codex = [i.bin / 'codex']
    run([*codex, 'plugin', 'marketplace', 'add', marketplace], env=i.env)
    run([*codex, 'plugin', 'add', 'figma@ai-setup-providers'], env=i.env)
    i.state['figma_revision'] = spec['revision']
    i.save()
