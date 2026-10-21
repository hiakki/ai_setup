"""Pinned OpenRig runtime and shared team entrypoint; no automatic agent launch."""
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile

from setup import ROOT, capture, run
from agentreach_runtime import write_launcher


def locations(i):
    spec = i.manifest['openrig']
    if not re.fullmatch(r'\d+\.\d+\.\d+', spec['version']):
        raise ValueError('OpenRig needs an exact version')
    root = i.home / '.local/share/ai-setup'
    return root / ('openrig-' + spec['version']), root / 'openrig-team'


def node_paths(i):
    system = {'Darwin': 'darwin', 'Linux': 'linux'}[platform.system()]
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64'}[platform.machine()]
    root = i.home / '.local/share/ai-setup' / f'node-v{i.manifest["openrig"]["node"]}-{system}-{arch}'
    return root / 'bin/node', root / 'lib/node_modules/npm/bin/npm-cli.js'


def check_package(i, prefix):
    package = prefix / 'node_modules/@openrig/cli'
    spec = i.manifest['openrig']
    meta = json.loads((package / 'package.json').read_text())
    lock = json.loads((prefix / 'package-lock.json').read_text())
    if (meta['version'] != spec['version'] or meta['name'] != '@openrig/cli' or
            lock['packages']['node_modules/@openrig/cli']['integrity'] != spec['integrity']):
        raise ValueError('OpenRig package identity/integrity mismatch')
    node, _ = node_paths(i)
    entry = package / 'dist/bin-wrapper.js'
    version = capture([node, entry, '--version'], env=i.env, timeout=30)
    if spec['version'] not in version.split():
        raise ValueError('OpenRig executable version mismatch: ' + repr(version))
    run([node, '-e', 'const D=require("better-sqlite3");const d=new D(":memory:");d.prepare("select 1").get();d.close()'],
        cwd=package, env=i.env, timeout=30)
    return entry


def ensure_linux_prerequisites(i):
    if platform.system() != 'Linux':
        return
    required = {'tmux': 'tmux', 'ps': 'procps', 'make': 'build-essential',
                'g++': 'build-essential', 'python3': 'python3'}
    missing = sorted({package for command, package in required.items()
                      if not shutil.which(command, path=i.env['PATH'])})
    if not missing:
        return
    if not shutil.which('apt-get', path=i.env['PATH']):
        raise ValueError('Install tmux, procps, Python 3, make and a C++ compiler, then rerun --only openrig')
    sudo = [] if os.geteuid() == 0 else ['sudo']
    run([*sudo, 'apt-get', 'update'], env=i.env, timeout=300)
    run([*sudo, 'apt-get', 'install', '-y', '--no-install-recommends', *missing],
        env=i.env, timeout=600)


def install(i):
    prefix, team = locations(i)
    for path in (prefix, team, i.home / '.agents/skills/openrig-team',
                 i.bin / ('ai-team.cmd' if i.windows else 'ai-team')):
        i.owned(path)
    if not i.windows:
        for name in ('rig', 'openrig-tui'):
            i.owned(i.bin / name)
        ensure_linux_prerequisites(i)
        if not shutil.which('tmux', path=i.env['PATH']):
            if platform.system() == 'Darwin' and shutil.which('brew', path=i.env['PATH']):
                run(['brew', 'install', 'tmux'], env=dict(i.env, HOMEBREW_NO_AUTO_UPDATE='1',
                    HOMEBREW_NO_INSTALL_CLEANUP='1'), timeout=600)
            elif platform.system() == 'Linux' and shutil.which('apt-get', path=i.env['PATH']):
                sudo = [] if os.geteuid() == 0 else ['sudo']
                run([*sudo, 'apt-get', 'update'], env=i.env, timeout=300)
                run([*sudo, 'apt-get', 'install', '-y', '--no-install-recommends', 'tmux'], env=i.env, timeout=300)
            else:
                raise ValueError('Install tmux using the OS package manager, then rerun --only openrig')
        from runtime import ensure_node
        system = {'Darwin': 'darwin', 'Linux': 'linux'}[platform.system()]
        arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64'}[platform.machine()]
        ensure_node(i, i.manifest['openrig']['node'], system, arch)
        node, npm = node_paths(i)
        env = dict(i.env, PATH=str(node.parent) + os.pathsep + i.env['PATH'])
        if not prefix.exists():
            with tempfile.TemporaryDirectory(prefix='openrig-install-', dir=prefix.parent) as tmp:
                staged = Path(tmp) / 'npm'
                run([node, npm, 'install', '--prefix', staged, '--ignore-scripts', '--no-audit',
                     '--no-fund', '--registry=https://registry.npmjs.org',
                     '@openrig/cli@' + i.manifest['openrig']['version']], env=env, timeout=600)
                # Only SQLite needs its native binary; do not run unrelated lifecycle hooks.
                run([node, npm, 'rebuild', '--prefix', staged, 'better-sqlite3'], env=env, timeout=600)
                check_package(i, staged)
                staged.rename(prefix)
            i.remember(prefix)
        entry = check_package(i, prefix)
        write_launcher(i, 'rig', [node, entry], search_path=node.parent)
        write_launcher(i, 'openrig-tui', [node, entry.parent.parent / 'tui/dist/main.js'], search_path=node.parent)
    else:
        print('OpenRig: installing native Windows SSH client entrypoint. Execution requires a macOS/Linux host; no WSL is installed.')
    with tempfile.TemporaryDirectory() as tmp:
        payload = Path(tmp) / 'team'
        payload.mkdir()
        for source, name in ((ROOT / 'ai_team.py', 'ai_team.py'),
                             (ROOT / 'config/openrig-roles.json', 'roles.json'),
                             (ROOT / 'config/ai-local.gitignore', 'ai-local.gitignore'),
                             (ROOT / 'docs/OPENRIG.md', 'README.md')):
            shutil.copy2(source, payload / name)
        i.copy_tree(payload, team)
    write_launcher(i, 'ai-team', [sys.executable, '-B', team / 'ai_team.py'])
    target = i.home / '.agents/skills/openrig-team'
    i.copy_tree(ROOT / 'custom/skills/openrig-team', target)
    i.link(i.home / '.claude/skills/openrig-team', target)
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.merge_text(path, (ROOT / 'config/OPENRIG.md').read_text(), 'openrig')
    i.state['openrig'] = {'version': i.manifest['openrig']['version'],
        'mode': 'ssh-client' if i.windows else 'local-runtime', 'auto_launch': False}
    i.save()
    verify(i)


def verify(i):
    prefix, team = locations(i)
    for path in (team, i.home / '.agents/skills/openrig-team',
                 i.bin / ('ai-team.cmd' if i.windows else 'ai-team')):
        i.owned(path)
        if not path.exists():
            raise ValueError('Missing OpenRig integration: ' + str(path))
    if not i.windows:
        i.owned(prefix)
        check_package(i, prefix)
    run([sys.executable, '-B', team / 'ai_team.py', 'roles'], env=i.env, timeout=30)
