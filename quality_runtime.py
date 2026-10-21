"""Pinned, on-demand quality CLIs; no hooks, scanning or browser services."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import sys
import tarfile
import tempfile
import zipfile

from setup import ROOT, capture, run, venv_python
from contextmode_runtime import runtime_paths


GUIDANCE = '''# Task-specific quality tools

For agent/skill evaluations, React performance, structural rewrite rules, API
contract testing, browser accessibility/visual checks or performance profiling,
read the global `development-quality` skill and only its relevant reference.
Vercel React and composition skills and Promptfoo evaluation/provider skills are
installed from pinned upstream sources. Prefer existing project tests first.
Use Codebase Memory first for code relationships; ast-grep complements it for
syntax patterns. Use RTK explicitly only; preserve raw failure evidence.
Installation does not authorize scans, paid model runs, source uploads, application
changes, browser/service startup, Storybook setup or RTK hooks. Never enable these
implicitly. App tests, baselines and reports remain app-owned. See
`docs/DEVELOPMENT_QUALITY.md` in ai_setup for versions and evidence limits.
'''


def target(i):
    system = 'Windows' if i.windows else platform.system()
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64', 'AMD64': 'x64'}.get(platform.machine())
    if system not in ('Darwin', 'Linux', 'Windows') or arch not in ('arm64', 'x64') or (system == 'Windows' and arch != 'x64'):
        raise ValueError('Quality tools require macOS/Linux x64 or ARM64, or native Windows x64')
    return system, arch


def version(value):
    if not re.fullmatch(r'\d+\.\d+\.\d+', value):
        raise ValueError('Quality tools require exact release versions')
    return value


def deduplicate_workflow(i):
    """Remove only a byte-equivalent standalone copy of the managed policy."""
    body = (ROOT / 'config/WORKFLOW_RULES.md').read_text(encoding='utf-8').strip()
    start, end = '<!-- ai-setup:workflow:start -->', '<!-- ai-setup:workflow:end -->'
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.safe(path)
        if not path.exists() or path.is_symlink():
            continue
        text = path.read_text(encoding='utf-8')
        if text.count(start) != 1 or text.count(end) != 1:
            continue
        before, tail = text.split(start, 1)
        managed, after = tail.split(end, 1)
        if managed.strip() != body:
            continue
        # Match complete paragraphs, not text inside an edited personal policy.
        pattern = r'(?m)(?<=\n\n)' + re.escape(body) + r'(?=\n\n|\n?$)'
        def remove_exact(value):
            return re.sub(pattern, '', '\n\n' + value)[2:]
        updated = remove_exact(before) + start + managed + end + remove_exact(after)
        if updated != text:
            i.backup(path)
            path.write_text(updated, encoding='utf-8')


def write_launcher(i, name, argv):
    env = {'PROMPTFOO_DISABLE_TELEMETRY': '1', 'SCHEMATHESIS_TELEMETRY': 'false',
           'CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    if i.windows:
        from windows_runtime import launcher
        content = launcher(argv).replace('setlocal DisableDelayedExpansion\n',
            'setlocal DisableDelayedExpansion\n' + ''.join(f'set "{k}={v}"\n' for k, v in env.items()))
        i.write(i.bin / (name + '.cmd'), content, 0o755)
    else:
        content = '#!/bin/sh\n' + ''.join(f'export {k}={shlex.quote(v)}\n' for k, v in env.items())
        i.write(i.bin / name, content + 'exec ' + ' '.join(shlex.quote(str(x)) for x in argv) + ' "$@"\n', 0o755)


def npm_package(i, name, spec, node, npm):
    ver = version(spec['version'])
    prefix = i.home / '.local/share/ai-setup' / (name.replace('@', '').replace('/', '-') + '-' + ver)
    native = None
    if name == 'promptfoo':
        system, arch = target(i)
        os_name = {'Darwin': 'darwin', 'Linux': 'linux', 'Windows': 'win32'}[system]
        tail = '-msvc' if i.windows else '-gnu' if system == 'Linux' else ''
        native = os_name + '-' + arch + tail
        binding = i.manifest['quality']['libsql']
        prefix = prefix.with_name(prefix.name + '-sqlite-' + version(binding['version']))
    i.owned(prefix)
    if not prefix.exists():
        prefix.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='quality-npm-', dir=prefix.parent) as tmp:
            staged = Path(tmp) / 'npm'
            env = dict(i.env, PATH=str(node.parent) + os.pathsep + i.env['PATH'],
                       PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1', PUPPETEER_SKIP_DOWNLOAD='true')
            args = [node, npm, 'install', '--prefix', staged, '--ignore-scripts', '--no-bin-links',
                    '--no-audit', '--no-fund', '--registry=https://registry.npmjs.org']
            if name == 'promptfoo':
                args.append('--omit=optional')
            packages = [name + '@' + ver]
            if native:
                packages.append('@libsql/' + native + '@' + binding['version'])
            run([*args, *packages], env=env)
            lock = json.loads((staged / 'package-lock.json').read_text())
            if lock['packages']['node_modules/' + name]['integrity'] != spec['integrity']:
                raise ValueError('Pinned npm integrity mismatch: ' + name)
            if native and lock['packages']['node_modules/@libsql/' + native]['integrity'] != binding['integrity'][native]:
                raise ValueError('Promptfoo SQLite binding integrity mismatch')
            staged.rename(prefix)
        i.remember(prefix)
    root = prefix / 'node_modules' / name
    data = json.loads((root / 'package.json').read_text())
    if data['name'] != name or data['version'] != ver:
        raise ValueError('Installed package identity mismatch: ' + name)
    return prefix, root


def install_rtk(i):
    system, arch = target(i)
    machine = 'aarch64' if arch == 'arm64' else 'x86_64'
    suffix = {'Darwin': 'apple-darwin', 'Windows': 'pc-windows-msvc',
              'Linux': 'unknown-linux-gnu' if arch == 'arm64' else 'unknown-linux-musl'}[system]
    triple = machine + '-' + suffix
    spec = i.manifest['quality']['rtk']
    ver = version(spec['version'])
    digest = spec['sha256'][triple]
    if not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('RTK requires a platform SHA256 pin')
    binary = i.bin / ('rtk.exe' if i.windows else 'rtk')
    i.owned(binary)
    expected = {'version': ver, 'sha256': digest, 'edition': 'oss'}
    if i.state.get('quality_rtk') == expected and binary.is_file():
        return [binary]
    i.bin.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='quality-rtk-', dir=i.bin) as tmp:
        archive = Path(tmp) / ('rtk.zip' if i.windows else 'rtk.tar.gz')
        from runtime import download
        asset = 'rtk-oss-' + triple + ('.zip' if i.windows else '.tar.gz')
        download(f'https://github.com/rtk-ai/rtk/releases/download/v{ver}/{asset}', archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError('RTK checksum mismatch; existing binary preserved')
        candidate = Path(tmp) / binary.name
        if i.windows:
            with zipfile.ZipFile(archive) as bundle:
                members = [m for m in bundle.infolist() if Path(m.filename).name in ('rtk.exe', 'rtk-oss.exe') and not m.is_dir()]
                if len(members) != 1 or (members[0].external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('RTK archive must contain one regular executable')
                with bundle.open(members[0]) as source, candidate.open('wb') as out:
                    shutil.copyfileobj(source, out)
        else:
            with tarfile.open(archive) as bundle:
                members = [m for m in bundle.getmembers() if Path(m.name).name in ('rtk', 'rtk-oss') and m.isfile()]
                if len(members) != 1:
                    raise ValueError('RTK archive must contain one regular executable')
                with bundle.extractfile(members[0]) as source, candidate.open('wb') as out:
                    shutil.copyfileobj(source, out)
            candidate.chmod(0o755)
        if ver not in capture([candidate, '--version'], env=i.env):
            raise ValueError('RTK executable version mismatch')
        candidate.replace(binary)
    i.remember(binary)
    i.state['quality_rtk'] = expected
    i.save()
    return [binary]


def install(i):
    system, arch = target(i)
    node, npm = runtime_paths(i)
    if i.windows:
        from windows_runtime import ensure_node
        ensure_node(i, i.manifest['node'])
    else:
        from runtime import ensure_node
        ensure_node(i, i.manifest['node'], {'Darwin': 'darwin', 'Linux': 'linux'}[system], arch)
    commands = {}
    for name, spec in i.manifest['quality']['npm'].items():
        prefix, root = npm_package(i, name, spec, node, npm)
        if name == 'promptfoo':
            commands['promptfoo'] = [node, root / 'dist/src/entrypoint.js']
        elif name == 'chrome-devtools-mcp':
            commands['chrome-devtools'] = [node, root / 'build/src/bin/chrome-devtools.js']
        else:
            os_name = {'Darwin': 'darwin', 'Linux': 'linux', 'Windows': 'win32'}[system]
            tail = '-msvc' if i.windows else '-gnu' if system == 'Linux' else ''
            binary = prefix / 'node_modules/@ast-grep' / f'cli-{os_name}-{arch}{tail}' / ('ast-grep.exe' if i.windows else 'ast-grep')
            commands['ast-grep'] = [binary]
    ver = version(i.manifest['quality']['schemathesis'])
    root = i.home / '.local/share/ai-setup' / ('schemathesis-' + ver)
    i.owned(root)
    if not root.exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='quality-python-', dir=root.parent) as tmp:
            staged = Path(tmp) / 'venv'
            run([sys.executable, '-m', 'venv', staged], env=i.env)
            run([venv_python(staged), '-m', 'pip', 'install', '--no-cache-dir', '--disable-pip-version-check',
                 '--index-url=https://pypi.org/simple', 'schemathesis==' + ver], env=i.env)
            staged.rename(root)
        i.remember(root)
    commands['schemathesis'] = [venv_python(root), '-c', 'from schemathesis.cli import schemathesis; schemathesis()']
    for name, argv in commands.items():
        write_launcher(i, name, argv)
    commands['rtk'] = install_rtk(i)
    # These maintained examples belong to this component; a targeted install
    # must not replace an unrelated, locally edited aggregate docs bundle.
    examples = i.home / '.local/share/ai-setup/quality'
    with tempfile.TemporaryDirectory(prefix='quality-guides-') as tmp:
        staged = Path(tmp) / 'guides'; staged.mkdir()
        for directory in ('evaluations', 'templates'):
            shutil.copytree(ROOT / directory, staged / directory,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copy2(ROOT / 'docs/DEVELOPMENT_QUALITY.md', staged / 'DEVELOPMENT_QUALITY.md')
        i.copy_tree(staged, examples)
    # Install the same skill into both clients without per-project copies.
    i.install_skill(ROOT, {'path': 'custom/skills/development-quality', 'name': 'development-quality'})
    for source_id in ('vercel-design', 'promptfoo-skills'):
        spec = i.spec(source_id)
        source = i.fetch(spec)
        for entry in spec['skills']:
            i.install_skill(source, entry)
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.merge_text(path, GUIDANCE, 'quality')
        routing = (ROOT / 'config/CENTRAL_ROUTING.md').read_text(encoding='utf-8')
        routing = routing.replace('{{REFERENCE}}', str(i.home / '.local/share/ai-setup/reference'))
        routing = routing.replace('{{DOCS}}', str(i.home / '.local/share/ai-setup/docs'))
        i.merge_text(path, routing, 'hub')
    deduplicate_workflow(i)
    i.state['quality'] = {'manifest': i.manifest['quality'],
                          'commands': {k: [str(x) for x in v] for k, v in commands.items()}}
    i.save()
    verify(i)


def verify(i):
    state = i.state.get('quality', {})
    if state.get('manifest') != i.manifest['quality']:
        raise ValueError('Quality tools are missing or outdated; rerun --only quality')
    env = dict(i.env, PROMPTFOO_DISABLE_TELEMETRY='1', PYTHONDONTWRITEBYTECODE='1')
    for name, argv in state['commands'].items():
        if not capture([*argv, '--help'], env=env, timeout=120):
            raise ValueError('Quality CLI returned no help: ' + name)
        suffix = '.exe' if name == 'rtk' else '.cmd'
        i.owned(i.bin / (name + (suffix if i.windows else '')))
