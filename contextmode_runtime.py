"""Pinned local Context Mode MCP, without plugin hooks or npm postinstall."""
import copy
import json
import os
from pathlib import Path
import platform
import re
import shlex
import tempfile
import tomllib

from setup import ROOT, capture, run

GUIDANCE = '''# Context Mode: bounded local output processing

The `context-mode` MCP is installed globally for large logs, test output and
documents that benefit from local indexing and focused retrieval. Use
`ctx_execute`/`ctx_execute_file` to compute a concise result, or `ctx_index` then
`ctx_search` for repeated questions about authorized material. Pass an explicit
timeout and working directory for commands; on Windows prefer JavaScript or
Python and absolute paths over assumptions about the shell.

Keep Codebase Memory first for code structure, Context7 for library documentation,
and direct file reads for small edits. Check original evidence before decisions;
search misses and compressed output are not proof of absence or success. Inspect
exit codes and failing tests, not just matched summary lines. Do not replace
Hindsight, Agent Wiki or canonical project docs with this local index.

This is not an OS security sandbox: execution has the user's filesystem/network
permissions. Existing scope, approvals and tool restrictions still apply. Do not
index credentials or unrelated projects, bypass denied tools, start background
services, use ctx_upgrade, or install capture/routing hooks without authorization.
No automatic transcript capture or cross-machine context synchronization is enabled.
Use ai_setup's pinned installer for updates. See `docs/CONTEXT_MODE.md` in the
central library for operation and verification.
'''


def configurations(i, node, entry):
    wrapper = i.home / '.local/share/ai-setup/context-mode-server.mjs'
    common = {'command': str(node), 'args': [str(wrapper), str(entry)]}
    storage = str(i.home / '.local/state/ai-setup/context-mode')
    return [
        (i.home / '.codex/config.toml', 'mcp_servers', dict(common, env={
            'CONTEXT_MODE_DIR': storage, 'CONTEXT_MODE_PLATFORM': 'codex'})),
        (i.home / '.claude.json', 'mcpServers', dict(common, type='stdio', env={
            'CONTEXT_MODE_DIR': storage, 'CONTEXT_MODE_PLATFORM': 'claude-code'})),
    ]


def configure(i, node, entry, *, check_only=False):
    """Preflight both clients; replace only an unchanged owned registration."""
    import tomlkit
    planned = []
    for path, key, expected in configurations(i, node, entry):
        i.safe(path)
        text = path.read_text(encoding='utf-8') if path.exists() else ''
        data = tomlkit.parse(text) if path.suffix == '.toml' else json.loads(text or '{}')
        name = path.relative_to(i.home).as_posix()
        old = data.get(key, {}).get('context-mode')
        previous = i.state.get('configuration', {}).get(name, {}).get(key, {}).get('context-mode')
        if old is not None and old != expected and (previous is None or old != previous):
            raise ValueError(f'Preserving existing context-mode settings in {path}; review before installing')
        data.setdefault(key, {})['context-mode'] = expected
        content = tomlkit.dumps(data) if path.suffix == '.toml' else json.dumps(data, indent=2) + '\n'
        planned.append((path, name, key, expected, content))
    if check_only:
        return
    for path, name, key, expected, content in planned:
        i.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        path.chmod(0o600)
        recorded = i.state.setdefault('configuration', {}).setdefault(name, {})
        recorded.setdefault(key, {})['context-mode'] = copy.deepcopy(expected)
    i.save()


def runtime_paths(i):
    if i.windows:
        from windows_runtime import node_root
        root = node_root(i, i.manifest['node'])
        return root / 'node.exe', root / 'node_modules/npm/bin/npm-cli.js'
    system = {'Darwin': 'darwin', 'Linux': 'linux'}.get(platform.system())
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64'}.get(platform.machine())
    if not system or not arch:
        raise ValueError('Context Mode supports macOS/Linux x64/arm64 and native Windows x64')
    root = i.home / '.local/share/ai-setup' / f'node-v{i.manifest["node"]}-{system}-{arch}'
    return root / 'bin/node', root / 'lib/node_modules/npm/bin/npm-cli.js'


def package_root(i):
    version = i.manifest['context_mode']['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Context Mode requires an exact npm release')
    return i.home / '.local/share/ai-setup' / ('context-mode-' + version)


def check_package(prefix, version):
    root = prefix / 'node_modules/context-mode'
    metadata = json.loads((root / 'package.json').read_text(encoding='utf-8'))
    if metadata.get('name') != 'context-mode' or metadata.get('version') != version:
        raise ValueError('Context Mode package differs from its pinned provider version')
    for name in ('server.bundle.mjs', 'cli.bundle.mjs', 'LICENSE'):
        if not (root / name).is_file():
            raise ValueError('Context Mode package is missing ' + name)
    return root


def install(i):
    prefix = package_root(i)
    node, npm = runtime_paths(i)
    entry = prefix / 'node_modules/context-mode/server.bundle.mjs'
    terminal = i.bin / ('context-mode.cmd' if i.windows else 'context-mode')
    wrapper = i.home / '.local/share/ai-setup/context-mode-server.mjs'
    configure(i, node, entry, check_only=True)
    i.owned(prefix)
    i.owned(terminal)
    i.owned(wrapper)
    if i.windows:
        from windows_runtime import ensure_node
        ensure_node(i, i.manifest['node'])
    else:
        from runtime import ensure_node
        system = {'Darwin': 'darwin', 'Linux': 'linux'}[platform.system()]
        arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64'}[platform.machine()]
        ensure_node(i, i.manifest['node'], system, arch)
    if capture([node, '--version'], env=i.env) != 'v' + i.manifest['node']:
        raise ValueError('Context Mode managed Node version differs from the manifest')
    # Require FTS5 without better-sqlite3's native build/lifecycle scripts.
    run([node, '-e', "const {DatabaseSync}=require('node:sqlite'); const d=new DatabaseSync(':memory:'); d.exec('CREATE VIRTUAL TABLE t USING fts5(text)'); d.close();"], env=i.env)
    version = i.manifest['context_mode']['version']
    if not prefix.exists():
        prefix.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='context-mode-stage-', dir=prefix.parent) as temp:
            staged = Path(temp) / 'npm'
            env = dict(i.env, PATH=str(node.parent) + os.pathsep + i.env['PATH'])
            run([node, npm, 'install', '--prefix', staged, '--ignore-scripts', '--no-bin-links',
                 '--registry=https://registry.npmjs.org', '--no-audit', '--no-fund',
                 'context-mode@' + version], env=env)
            check_package(staged, version)
            lock = json.loads((staged / 'package-lock.json').read_text(encoding='utf-8'))
            if lock['packages']['node_modules/context-mode']['integrity'] != i.manifest['context_mode']['integrity']:
                raise ValueError('Context Mode npm integrity differs from the reviewed release')
            staged.rename(prefix)
        i.remember(prefix)
    root = check_package(prefix, version)
    if i.windows:
        from windows_runtime import launcher
        text = launcher([node, root / 'cli.bundle.mjs'])
    else:
        text = '#!/bin/sh\nexec ' + shlex.quote(str(node)) + ' ' + shlex.quote(str(root / 'cli.bundle.mjs')) + ' "$@"\n'
    i.write(terminal, text, 0o755)
    i.write(wrapper, (ROOT / 'context_mode_server.mjs').read_text(encoding='utf-8'))
    configure(i, node, entry)
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.merge_text(path, GUIDANCE, marker='contextmode')
    i.state['contextmode'] = {'version': version, 'node': str(node), 'entry': str(entry),
                             'hooks': False, 'lifecycle_scripts': False}
    i.save()
    verify(i)


def verify(i):
    state = i.state.get('contextmode', {})
    version = i.manifest['context_mode']['version']
    if state.get('version') != version:
        raise ValueError('Context Mode is missing or outdated; rerun --only contextmode')
    prefix = package_root(i)
    i.owned(prefix)
    root = check_package(prefix, version)
    node, _ = runtime_paths(i)
    for path, key, expected in configurations(i, node, root / 'server.bundle.mjs'):
        content = path.read_text(encoding='utf-8')
        actual = tomllib.loads(content) if path.suffix == '.toml' else json.loads(content)
        if actual.get(key, {}).get('context-mode') != expected:
            raise ValueError(f'Context Mode registration changed in {path}; review before rerunning')
    # Upstream has no --version command: unknown arguments enter stdio mode.
    if 'context-mode' not in capture([node, root / 'cli.bundle.mjs', '--help'], env=i.env):
        raise ValueError('Context Mode CLI help did not load')
