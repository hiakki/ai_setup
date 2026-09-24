"""Native Windows runtimes; Git Bash is used only for providers' shell scripts.

All MCP/client subprocesses use Windows executables directly, never WSL or a
cmd.exe intermediary. Third-party code is downloaded from its pinned provider.
"""
import contextlib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import tempfile
import time
import tomllib
import zipfile

from setup import capture, run
from runtime import download, merge, merge_config


def verify_checksum(archive, checksums, name):
    matches = [parts[0].lower() for line in checksums.splitlines()
               if len(parts := line.split()) == 2 and parts[1].lstrip('*') == name]
    if (len(matches) != 1 or not re.fullmatch('[0-9a-f]{64}', matches[0]) or
            hashlib.sha256(archive.read_bytes()).hexdigest() != matches[0]):
        raise ValueError(f'Checksum mismatch or missing digest for {name}; retry the provider download')


def extract_zip(archive, destination):
    """Validate Windows' namespace before writing any official archive entry."""
    seen = set()
    devices = {'con', 'prn', 'aux', 'nul', *(f'com{x}' for x in range(1, 10)),
               *(f'lpt{x}' for x in range(1, 10))}
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            name = entry.filename.replace('\\', '/')
            parts = name.rstrip('/').split('/')
            if (name.startswith('/') or ':' in name or not parts or
                    any(p in ('', '.', '..') or p.endswith(('.', ' ')) or
                        p.split('.')[0].lower() in devices for p in parts) or
                    (entry.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError(f'Unsafe Windows archive entry: {name}; use a valid provider release')
            key = '/'.join(parts).casefold()
            if key in seen:
                raise ValueError(f'Case-conflicting archive entry: {name}; use a valid provider release')
            seen.add(key)
        destination.mkdir(parents=True, exist_ok=True)
        for entry in z.infolist():
            target = destination.joinpath(*PurePosixPath(entry.filename.replace('\\', '/')).parts)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(entry) as src, target.open('wb') as dst:
                    shutil.copyfileobj(src, dst)


def node_root(i, version):
    # The bootstrap currently supports native x64 Windows.
    return i.home / '.local/share/ai-setup' / f'node-v{version}-win-x64'


def ensure_node(i, version):
    root = node_root(i, version)
    i.safe(root)
    if not (root / 'node.exe').exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root.parent) as directory:
            tmp = Path(directory)
            name = root.name + '.zip'
            base = f'https://nodejs.org/dist/v{version}/'
            download(base + name, tmp / name)
            download(base + 'SHASUMS256.txt', tmp / 'checksums')
            verify_checksum(tmp / name, (tmp / 'checksums').read_text(encoding='utf-8'), name)
            extract_zip(tmp / name, tmp / 'extracted')
            (tmp / 'extracted' / root.name).rename(root)
    if capture([root / 'node.exe', '--version'], env=i.env) != 'v' + version:
        raise ValueError('Managed Node version differs from the manifest; preserve the changed installation before retrying')
    return root


def command(i, name):
    """Return a native argv, including a Node entrypoint when the CLI is JS."""
    node = node_root(i, i.manifest['node']) / 'node.exe'
    prefix = i.home / '.local/share/ai-setup/npm/node_modules'
    scripts = {'codex': '@openai/codex/bin/codex.js',
               'claude': '@anthropic-ai/claude-code/cli.js',
               'skills': 'skills/bin/cli.mjs',
               'playwright-mcp': '@playwright/mcp/cli.js'}
    if name in scripts:
        return [node, prefix / scripts[name]]
    if name in ('npm', 'npx'):
        return [node, node.parent / 'node_modules/npm/bin' / ('npm-cli.js' if name == 'npm' else 'npx-cli.js')]
    if name == 'graft':
        return [node_root(i, i.manifest['graft_node']) / 'node.exe',
                i.home / '.local/share/ai-setup/graft-npm/node_modules/@nanonets/graft/dist/cli.js']
    return [i.bin / (name + '.exe')]


def executable(i, name):
    return i.bin / (name + ('.cmd' if name in ('npm', 'npx', 'codex', 'claude', 'skills', 'graft', 'playwright-mcp') else '.exe'))


def launcher(argv):
    def quote(value):
        value = str(value)
        if any(c in value for c in ('"', '\n', '\r')):
            raise ValueError('Windows launcher path contains a quote or newline; choose a normal installation directory')
        return '"' + value.replace('%', '%%') + '"'
    return ('@echo off\nsetlocal DisableDelayedExpansion\n' +
            ' '.join(quote(value) for value in argv) + ' %*\nexit /b %errorlevel%\n')


def terminal_launchers(i, names):
    for name in names:
        argv = command(i, name)
        i.write(i.bin / (name + '.cmd'), launcher(argv))
        # Git Bash providers need a POSIX launcher as well as the PowerShell/cmd one.
        i.write(i.bin / name, '#!/bin/sh\nexec ' +
                ' '.join(shlex.quote(Path(arg).as_posix()) for arg in argv) + ' "$@"\n', 0o755)


def git_bash(i):
    explicit = i.env.get('CLAUDE_CODE_GIT_BASH_PATH')
    candidates = [Path(explicit)] if explicit else []
    git = shutil.which('git', path=i.env['PATH'])
    if git:
        candidates.extend([Path(git).parent.parent / 'bin/bash.exe', Path(git).parent / 'bash.exe'])
    candidates.append(i.home / '.local/share/ai-setup/bootstrap/git/bin/bash.exe')
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ValueError('Git Bash was not found; rerun install.ps1 to install Git for Windows (WSL is not needed)')


def bash_env(i):
    return dict(i.env, HOME=i.home.as_posix(), CODEX_HOME=(i.home / '.codex').as_posix(),
                CLAUDE_CODE_GIT_BASH_PATH=str(git_bash(i)))


def runtime(i):
    node = ensure_node(i, i.manifest['node'])
    i.link(i.bin / 'node.exe', node / 'node.exe')
    prefix = i.home / '.local/share/ai-setup/npm'
    packages = {name: version for name, version in i.manifest['npm'].items() if name != '@nanonets/graft'}
    if i.state.get('windows_npm') != packages:
        run([*command(i, 'npm'), 'install', '--global', '--prefix', prefix,
             *(f'{name}@{version}' for name, version in packages.items())], env=i.env)
        i.state['windows_npm'] = packages
        i.save()
    for name in ('bun', 'bunx'):
        i.link(i.bin / (name + '.exe'), prefix / 'node_modules/bun/bin' / (name + '.exe'))
    graft_node = ensure_node(i, i.manifest['graft_node'])
    graft_version = i.manifest['npm']['@nanonets/graft']
    if i.state.get('windows_graft_runtime') != graft_version:
        env = dict(i.env, PATH=str(graft_node) + os.pathsep + i.env['PATH'], DO_NOT_TRACK='1')
        run([graft_node / 'node.exe', graft_node / 'node_modules/npm/bin/npm-cli.js',
             'install', '--global', '--prefix', i.home / '.local/share/ai-setup/graft-npm',
             '@nanonets/graft@' + graft_version], env=env)
        i.state['windows_graft_runtime'] = graft_version
        i.save()
    terminal_launchers(i, ('npm', 'npx', 'codex', 'claude', 'graft', 'skills', 'playwright-mcp'))
    for name in ('codex', 'claude', 'graft', 'skills', 'bun'):
        run([*command(i, name), '--version'], env=i.env)
    binary = i.bin / 'codebase-memory-mcp.exe'
    expected = i.manifest['codebase_memory_version']
    if not binary.exists():
        spec = i.spec('codebase-memory')
        installer = i.home / '.local/share/ai-setup/installers/codebase-memory.ps1'
        i.safe(installer)
        installer.parent.mkdir(parents=True, exist_ok=True)
        download('https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/' + spec['revision'] + '/install.ps1', installer)
        if hashlib.sha256(installer.read_bytes()).hexdigest() != i.manifest['codebase_memory_windows_installer_sha256']:
            raise ValueError('Codebase Memory installer checksum mismatch; retry the provider download')
        env = dict(i.env, CBM_ARCH='amd64',
                   CBM_DOWNLOAD_URL=f'https://github.com/DeusData/codebase-memory-mcp/releases/download/v{expected}')
        run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', installer,
             '--skip-config', '--dir=' + str(i.bin)], env=env)
        i.remember(binary)
    else:
        i.owned(binary)
    if expected not in capture([binary, '--version'], env=i.env):
        raise ValueError('Codebase Memory version mismatch; preserve the changed binary before retrying')
    install_ffmpeg(i)


def install_ffmpeg(i):
    spec = i.manifest['windows_ffmpeg']
    root = i.home / '.local/share/ai-setup' / ('ffmpeg-' + spec['version'])
    i.safe(root)
    if not (root / 'bin/ffmpeg.exe').exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root.parent) as directory:
            tmp = Path(directory)
            name = f'ffmpeg-{spec["version"]}-essentials_build.zip'
            download(f'https://github.com/GyanD/codexffmpeg/releases/download/{spec["version"]}/' + name, tmp / name)
            verify_checksum(tmp / name, spec['sha256'] + '  ' + name, name)
            extract_zip(tmp / name, tmp / 'extracted')
            extracted = list((tmp / 'extracted').iterdir())
            if len(extracted) != 1 or not (extracted[0] / 'bin/ffmpeg.exe').exists():
                raise ValueError('Unexpected FFmpeg archive layout; check the pinned Windows provider build')
            extracted[0].rename(root)
    for name in ('ffmpeg', 'ffprobe'):
        i.link(i.bin / (name + '.exe'), root / 'bin' / (name + '.exe'))
    run([i.bin / 'ffmpeg.exe', '-version'], env=i.env)


def blog_renderer_adapter(i, source):
    """Adapt the pinned renderer's POSIX-only open while retaining link refusal."""
    path = source / 'scripts/blog_render.py'
    original = '        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)'
    replacement = '''        # ai-setup: Windows has no O_NOFOLLOW. Check the opened file identity.
        before = os.lstat(path)
        if (not stat.S_ISREG(before.st_mode) or
                getattr(before, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
            raise ValueError(f"refusing link or non-regular file: {path}")
        fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            if not os.path.samestat(before, os.fstat(fd)):
                raise ValueError(f"source changed while opening: {path}")
        except BaseException:
            os.close(fd)
            raise'''
    text = path.read_text(encoding='utf-8')
    if replacement not in text:
        if text.count(original) != 1:
            raise ValueError('Pinned blog renderer changed; review its Windows read adapter')
        # fetch() has already checked the provider revision and any recorded diff.
        i.safe(path)
        path.write_text(text.replace(original, replacement, 1), encoding='utf-8')
    i.remember(path)
    i.state.setdefault('generated_sources', {})['claude-blog'] = capture(['git', '-C', source, 'diff', 'HEAD'])
    i.save()


def gstack(i):
    source = i.fetch(i.spec('gstack'))
    if 'gstack' in i.state['completed']:
        i.verify()
        gstack_skill_names(i)
        return
    for folder in (i.home / '.claude/skills', i.home / '.codex/skills', i.home / '.agents/skills'):
        for path in folder.glob('gstack*'):
            i.owned(path)
    claude = i.home / '.claude/skills/gstack'
    i.link(claude, source)
    env = dict(bash_env(i), GSTACK_SKIP_COREUTILS='1', GSTACK_SKIP_GBRAIN_REGEN='1',
               GSTACK_SKIP_FONTS='1', GSTACK_SKIP_ASIDE='1')
    flags = ['--prefix', '--no-team', '--no-plan-tune-hooks', '--no-timeline-stop-hook']
    try:
        for host in ('claude', 'codex'):
            run([git_bash(i), (claude / 'setup').as_posix(), '--host', host, *flags],
                cwd=source, env=env, stdin=subprocess.DEVNULL)
        run([git_bash(i), (source / 'bin/gstack-config').as_posix(), 'set', 'auto_upgrade', 'false'], env=env)
        run([git_bash(i), (source / 'bin/gstack-patch-names').as_posix(), '.agents/skills', 'true'], cwd=source, env=env)
        for path in sorted((i.home / '.codex/skills').glob('gstack-*')):
            if not (path / 'SKILL.md').exists():
                raise ValueError(f'Generated gstack skill missing: {path}; rerun provider setup')
            target = i.home / '.agents/skills' / path.name
            i.copy_tree(path, target)
            # These are the exact fresh provider-owned copies, not pre-existing user paths.
            if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
                path.rmdir() if getattr(path, 'is_junction', lambda: False)() else path.unlink()
            else:
                shutil.rmtree(path)
        i.write(i.home / '.agents/skills/gstack/SKILL.md', (source / '.agents/skills/gstack/SKILL.md').read_text(encoding='utf-8'))
        # The Codex runtime must expose binaries/assets without a second skill tree.
        runtime_adapter(i, source)
        gstack_skill_names(i)
    finally:
        # Remember only directories checked for ownership before provider setup.
        # A provider interruption remains resumable, without adopting unrelated files.
        for folder in (i.home / '.claude/skills', i.home / '.codex/skills'):
            for path in folder.glob('gstack*'):
                i.remember(path)
        i.state.setdefault('generated_sources', {})['gstack'] = capture(['git', '-C', source, 'diff', 'HEAD'])
        i.save()


def gstack_skill_names(i):
    """Windows provider copies need the same names as their prefixed folders."""
    for folder in sorted((i.home / '.agents/skills').glob('gstack-*')):
        if folder.relative_to(i.home).as_posix() not in i.state['files']:
            continue
        i.owned(folder)
        path = folder / 'SKILL.md'
        text = path.read_text(encoding='utf-8')
        updated, count = re.subn(r'(?m)^name:.*$', 'name: ' + folder.name, text, count=1)
        if count != 1:
            raise ValueError(f'Missing gstack skill name: {path}')
        if updated != text:
            path.write_text(updated, encoding='utf-8')
            i.remember(folder)


def runtime_adapter(i, source):
    """Replace the generated root without ever traversing/removing its links."""
    adapter = i.home / '.codex/skills/gstack'
    if adapter.exists():
        # Caller has established this is provider output in our installation.
        i.remember(adapter)
        backup = i.state_dir / ('gstack-runtime-adapter-' + str(time.time_ns()))
        adapter.rename(backup)
        prefix = adapter.relative_to(i.home).as_posix()
        for key in list(i.state['files']):
            if key == prefix or key.startswith(prefix + '/'):
                del i.state['files'][key]
    adapter.mkdir(parents=True, exist_ok=True)
    for name in ('bin', 'scripts', 'setup', 'package.json', 'lib', 'ETHOS.md'):
        if (source / name).exists():
            i.link(adapter / name, source / name)
    for name in ('browse', 'design', 'make-pdf'):
        if (source / name / 'dist').exists():
            i.link(adapter / name / 'dist', source / name / 'dist')
    i.remember(adapter)


def relocate(value, old, new):
    if isinstance(value, dict):
        return {key: relocate(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [relocate(item, old, new) for item in value]
    if isinstance(value, str):
        return value.replace(str(old), str(new)).replace(str(old).replace('\\', '/'), str(new).replace('\\', '/'))
    return value


def integrations(i):
    if 'integrations' not in i.state['completed']:
        stage = i.state_dir / 'provider-integration-home'
        for directory in ('.codex', '.claude'):
            (stage / directory).mkdir(parents=True, exist_ok=True)
        env = dict(i.env, HOME=str(stage), USERPROFILE=str(stage), CODEX_HOME=str(stage / '.codex'),
                   APPDATA=str(stage / 'AppData/Roaming'), LOCALAPPDATA=str(stage / 'AppData/Local'),
                   XDG_CONFIG_HOME=str(stage / '.config'), XDG_CACHE_HOME=str(stage / '.cache'),
                   XDG_DATA_HOME=str(stage / '.local/share'), XDG_STATE_HOME=str(stage / '.local/state'))
        # Upstream --skip-binary explicitly leaves both the executable and PATH
        # untouched. Generate only our requested clients in the isolated home.
        run([*command(i, 'codebase-memory-mcp'), 'install', '-y', '--skip-binary',
             '--clients=claude,codex', '--dir=' + str(i.bin)], env=env)
        bootstrap = stage / 'graft-bootstrap'
        bootstrap.mkdir(exist_ok=True)
        run(['git', 'init', '-q', bootstrap], env=env)
        run([*command(i, 'graft'), 'init', bootstrap, '--agents', 'agents', 'claude'], env=env)
        local_skill = bootstrap / '.claude/skills/graft'
        if local_skill.exists() and not (stage / '.claude/skills/graft').exists():
            shutil.copytree(local_skill, stage / '.claude/skills/graft')
        for directory in ('.claude', '.codex', '.agents'):
            for path in sorted((stage / directory).rglob('*')):
                if not path.is_file() or path.name in ('config.toml', 'hooks.json', 'settings.json'):
                    continue
                rel = path.relative_to(stage)
                if any(part in ('logs', 'sessions', '.git') for part in rel.parts):
                    continue
                text = relocate(path.read_text(encoding='utf-8'), stage, i.home)
                dest = i.home / rel
                if path.name in ('AGENTS.md', 'CLAUDE.md'):
                    i.merge_text(dest, text, 'provider-instructions')
                else:
                    i.write(dest, text)
        path = stage / '.codex/config.toml'
        codex = relocate(tomllib.loads(path.read_text(encoding='utf-8')), stage, i.home) if path.exists() else {}
        hooks = stage / '.codex/hooks.json'
        if hooks.exists():
            codex = merge(codex, relocate(json.loads(hooks.read_text(encoding='utf-8')), stage, i.home))
        if (i.home / '.codex/hooks.json').exists():
            raise ValueError('Existing ~/.codex/hooks.json: consolidate its hooks into config.toml before importing provider hooks')
        # Replace only the newly generated server stanzas with native direct argv.
        codex.pop('mcp_servers', None)
        merge_config(i, i.home / '.codex/config.toml', codex)
        path = stage / '.claude/settings.json'
        if path.exists():
            merge_config(i, i.home / '.claude/settings.json',
                         relocate(json.loads(path.read_text(encoding='utf-8')), stage, i.home))
    if not i.state.get('cbm_configured'):
        for key, value in [('auto_index', 'false'), ('auto_watch', 'true'), ('ui_enabled', 'true'), ('ui_port', '9749')]:
            run([*command(i, 'codebase-memory-mcp'), 'config', 'set', key, value], env=i.env)
        i.state['cbm_configured'] = True
        i.save()
    codex_path = i.home / '.codex/config.toml'
    claude_path = i.home / '.claude.json'
    codex = tomllib.loads(codex_path.read_text(encoding='utf-8')) if codex_path.exists() else {}
    claude = json.loads(claude_path.read_text(encoding='utf-8')) if claude_path.exists() else {}
    codex_playwright = codex.get('mcp_servers', {}).get('playwright', {})
    claude_playwright = claude.get('mcpServers', {}).get('playwright', {})
    existing = next((spec for spec in (codex_playwright, claude_playwright) if spec.get('command')), None)
    if existing:
        print('Reusing existing Playwright MCP command and browser; skipping browser download.')
        # Share the launch settings with a client that has no entry of its own.
        playwright_spec = {key: existing[key] for key in ('command', 'args', 'env') if key in existing}
    else:
        node = command(i, 'node')[0]
        playwright = i.home / '.local/share/ai-setup/npm/node_modules/@playwright/mcp'
        # Apply the timeout before connecting, including in Playwright's forked workers.
        download_timeout = Path(__file__).parent / 'config/playwright-download-timeout.cjs'
        run([node, '--require', download_timeout,
             playwright / 'node_modules/playwright/cli.js', 'install', 'chromium'], env=i.env)
        browser = capture([node, '-e', "console.log(require('playwright').chromium.executablePath())"], cwd=playwright, env=i.env)
        config = i.home / '.config/ai-setup/playwright.json'
        i.write(config, json.dumps({'browser': {'browserName': 'chromium', 'isolated': True,
                'launchOptions': {'executablePath': browser, 'headless': True, 'chromiumSandbox': True}}}, indent=2) + '\n')
        argv = command(i, 'playwright-mcp')
        playwright_spec = {'command': str(argv[0]), 'args': [*map(str, argv[1:]), '--config', str(config)],
                          'env': {'PATH': i.env['PATH'], 'PLAYWRIGHT_BROWSERS_PATH': i.env['PLAYWRIGHT_BROWSERS_PATH']}}
    servers = {}
    for name, args in [('codebase-memory-mcp', []), ('graft', ['mcp'])]:
        argv = command(i, name)
        servers[name] = {'command': str(argv[0]), 'args': [*map(str, argv[1:]), *args],
                         'env': {'PATH': i.env['PATH'], 'PLAYWRIGHT_BROWSERS_PATH': i.env['PLAYWRIGHT_BROWSERS_PATH']}}
    servers['figma'] = {'url': 'https://mcp.figma.com/mcp'}
    claude_servers = {name: dict(spec, type='http' if 'url' in spec else 'stdio') for name, spec in servers.items()}
    if not codex_playwright:
        servers['playwright'] = playwright_spec
    if not claude_playwright:
        claude_servers['playwright'] = dict(playwright_spec, type='stdio')
    for path, section, incoming, current in (
            (codex_path, 'mcp_servers', servers, codex),
            (claude_path, 'mcpServers', claude_servers, claude)):
        recorded = i.state.get('configuration', {}).get(path.relative_to(i.home).as_posix(), {}).get(section, {})
        for name in ('codebase-memory-mcp', 'graft'):
            # PATH changes between terminals (including after our PATH setup).
            # Reuse the installed value; retain conflict checks for local edits.
            configured_env = current.get(section, {}).get(name, {}).get('env', {})
            recorded_env = recorded.get(name, {}).get('env', {})
            installed_path = recorded_env.get('PATH', configured_env.get('PATH', i.env['PATH']))
            incoming[name]['env'] = dict(incoming[name]['env'], PATH=installed_path)
        merge_config(i, path, {section: incoming})
    trust_generated_hooks(i)


def trust_generated_hooks(i):
    from smoke import RPC
    cwd = i.state_dir / 'client-check'
    cwd.mkdir(exist_ok=True)
    path = i.home / '.codex/config.toml'
    planned = i.state.get('configuration', {}).get(path.relative_to(i.home).as_posix(), {}).get('hooks', {})
    expected = {(event[0].lower() + event[1:], entry.get('matcher'),
                 hook.get('command_windows', hook['command']))
                for event, entries in planned.items() if isinstance(entries, list)
                for entry in entries for hook in entry.get('hooks', []) if 'command' in hook}
    with contextlib.closing(RPC([*map(str, command(i, 'codex')), 'app-server', '--listen', 'stdio://'],
                               i.env, cwd, codex=True)) as rpc:
        result = rpc.call('hooks/list', {'cwds': [str(cwd)]})
    state = {}
    discovered = set()
    for entry in result['data']:
        if entry.get('errors'):
            raise ValueError('Codex rejected generated hooks; review config.toml: ' + str(entry['errors']))
        for hook in entry['hooks']:
            identity = (hook['eventName'], hook.get('matcher'), hook.get('command'))
            if Path(hook['sourcePath']) == path and identity in expected:
                state[hook['key']] = {'trusted_hash': hook['currentHash']}
                discovered.add(identity)
    if expected - discovered:
        raise ValueError('Codex did not discover every generated hook; review hooks/list before retrying')
    merge_config(i, path, {'hooks': {'state': state}})


def figma(i):
    if 'figma' in i.state['completed']:
        return
    spec = i.manifest['figma']
    source = i.fetch({'id': 'openai-plugins', 'url': 'https://github.com/' + spec['repository'] + '.git',
                      'revision': spec['revision'], 'sparse': ['plugins/figma']})
    marketplace = i.home / '.local/share/ai-setup/marketplace'
    i.copy_tree(source / 'plugins/figma', marketplace / 'plugins/figma')
    registry = {'name': 'ai-setup-providers', 'plugins': [{'name': 'figma',
                'source': {'source': 'local', 'path': './plugins/figma'},
                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}}]}
    i.write(marketplace / '.agents/plugins/marketplace.json', json.dumps(registry, indent=2) + '\n')
    run([*command(i, 'codex'), 'plugin', 'marketplace', 'add', marketplace], env=i.env)
    run([*command(i, 'codex'), 'plugin', 'add', 'figma@ai-setup-providers'], env=i.env)
