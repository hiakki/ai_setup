"""Optional, browser-free SkillUI installation from its pinned npm provider."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import tempfile

from setup import capture, run


def runtime_commands(i):
    """Reuse Node and npm without installing the unrelated default components."""
    if i.windows:
        from windows_runtime import node_root
        root = node_root(i, i.manifest['node'])
        node = root / 'node.exe'
        npm = root / 'node_modules/npm/bin/npm-cli.js'
        if node.is_file() and npm.is_file():
            result = (node, [node, npm])
        else:
            result = None
    else:
        result = None
    if result is None:
        node = shutil.which('node', path=i.env['PATH'])
        npm = shutil.which('npm', path=i.env['PATH'])
        if not node or not npm:
            raise ValueError('SkillUI requires Node.js 18+ and npm; install the runtime component first')
        node, npm = Path(node).resolve(), Path(npm).resolve()
        # npm.cmd sits next to node_modules on native Windows. Invoke its JS
        # entrypoint directly so spaces and shell metacharacters remain data.
        npm_js = npm.parent / 'node_modules/npm/bin/npm-cli.js'
        result = (node, [node, npm_js] if i.windows and npm_js.is_file() else [npm])
    version = capture([result[0], '--version'], env=i.env)
    match = re.fullmatch(r'v(\d+)\.\d+\.\d+', version)
    if not match or int(match[1]) < 18:
        raise ValueError('SkillUI requires Node.js 18+; install the runtime component first')
    return result


def package_root(i, prefix):
    return prefix / ('node_modules/skillui' if i.windows else 'lib/node_modules/skillui')


def check_package(i, prefix, version):
    root = package_root(i, prefix)
    metadata = json.loads((root / 'package.json').read_text(encoding='utf-8'))
    if metadata.get('name') != 'skillui' or metadata.get('version') != version:
        raise ValueError('SkillUI package does not match the pinned provider version')
    entry = root / 'dist/cli.js'
    if not entry.is_file():
        raise ValueError('SkillUI package is missing its CLI entrypoint')
    return entry


def install(i):
    version = i.manifest['optional_npm']['skillui']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('SkillUI must use an exact npm release version')
    node, npm = runtime_commands(i)
    prefix = i.home / '.local/share/ai-setup' / ('skillui-' + version)
    terminal = i.bin / ('skillui.cmd' if i.windows else 'skillui')
    # Refuse collisions before downloading or touching either installation.
    i.owned(prefix)
    i.owned(terminal)
    if not prefix.exists():
        prefix.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='skillui-stage-', dir=prefix.parent) as temporary:
            staged = Path(temporary) / 'npm'
            env = dict(i.env, PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1',
                       PATH=str(node.parent) + os.pathsep + i.env['PATH'])
            run([*npm, 'install', '--global', '--prefix', staged,
                 '--registry=https://registry.npmjs.org', '--no-audit', '--no-fund',
                 'skillui@' + version], env=env)
            entry = check_package(i, staged, version)
            run([node, entry, '--help'], env=env)
            staged.rename(prefix)
        i.remember(prefix)
    entry = check_package(i, prefix, version)
    if i.windows:
        from windows_runtime import launcher
        text = launcher([node, entry])
    else:
        text = '#!/bin/sh\nexec ' + shlex.quote(str(node)) + ' ' + shlex.quote(str(entry)) + ' "$@"\n'
    i.write(terminal, text, 0o755)
    i.state['skillui'] = {'version': version, 'node': str(node)}
    i.save()
    guidance = (
        f'SkillUI is installed at `{terminal}` for extracting design tokens and reusable '
        'UI context from an authorized local project. Run `skillui --help` first. '
        'Example: `skillui --dir ./my-app --out ./.agents/skillui --name my-app --format design-md`. '
        'Keep generated context inside that project and ignored by Git; review it before use. '
        'The default local directory workflow needs no browser or API key. '
        'Browser/ultra mode is optional and requires separately configured Playwright; '
        'installation does not authorize fetching sites or scanning unrelated projects.'
    )
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.merge_text(path, guidance, marker='skillui')
    verify(i)


def verify(i):
    state = i.state.get('skillui')
    version = i.manifest['optional_npm']['skillui']
    if not state or state.get('version') != version:
        raise ValueError('SkillUI installation is missing or its pinned version changed; rerun the skillui component')
    prefix = i.home / '.local/share/ai-setup' / ('skillui-' + version)
    i.owned(prefix)
    entry = check_package(i, prefix, version)
    run([state['node'], entry, '--help'], env=i.env)
