"""Pinned Agent Reach and OpenCLI, shared across projects without account setup."""
import json
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import tempfile
import tomllib

from setup import ROOT, capture, run, venv_python
from contextmode_runtime import runtime_paths


def paths(i):
    spec = i.manifest['agent_reach']
    revision = i.spec('agent-reach')['revision']
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Agent Reach requires an immutable provider commit')
    for version in (spec['version'], spec['yt_dlp'], spec['feedparser'], spec['opencli']['version']):
        if not re.fullmatch(r'\d+\.\d+\.\d+', version):
            raise ValueError('Agent Reach dependencies require exact versions')
    dependency_id = hashlib.sha256((spec['yt_dlp'] + ':' + spec['feedparser']).encode()).hexdigest()[:12]
    root = i.home / '.local/share/ai-setup' / ('agent-reach-' + spec['version'] + '-' + revision[:12] + '-' + dependency_id)
    npm = i.home / '.local/share/ai-setup' / ('agent-reach-opencli-' + spec['opencli']['version'])
    return root, venv_python(root), npm


def command(i):
    return [paths(i)[1], '-B', '-c', 'from agent_reach.cli import main; main()']


def write_launcher(i, name, argv, *, search_path=None, ci=False):
    if i.windows:
        from windows_runtime import launcher
        content = launcher(argv)
        environment = 'set "PYTHONUTF8=1"\n'
        if search_path:
            value = str(search_path)
            if any(c in value for c in ('"', '\r', '\n')):
                raise ValueError('Unsupported launcher path')
            environment += 'set "PATH=' + value.replace('%', '%%') + ';%PATH%"\n'
        if ci:
            environment += 'set "CI=1"\n'
        content = content.replace('setlocal DisableDelayedExpansion\n',
                                  'setlocal DisableDelayedExpansion\n' + environment)
        i.write(i.bin / (name + '.cmd'), content, 0o755)
    else:
        content = '#!/bin/sh\nexport PYTHONUTF8=1\n'
        if search_path:
            content += 'export PATH=' + shlex.quote(str(search_path)) + ':"$PATH"\n'
        if ci:
            content += 'export CI=1\n'
        i.write(i.bin / name, content + 'exec ' + ' '.join(shlex.quote(str(x)) for x in argv) + ' "$@"\n', 0o755)


def install_skill(i, source):
    import yaml
    def adapt(staged):
        original = (staged / 'SKILL_en.md').read_text(encoding='utf-8')
        _, front, body = original.split('---', 2)
        meta = yaml.safe_load(front)
        if meta.get('name') != 'agent-reach':
            raise ValueError('Agent Reach provider skill identity changed')
        meta['description'] = ('Research social-platform discussions, available video subtitles, RSS and '
                               'public pages using Agent Reach adapters. Use when platform-specific access '
                               'adds value; prefer existing web tools and Context7 for ordinary lookups.')
        universal = ('16 platforms, multiple backends each. **When this skill exists, use it for\n'
                     'these platforms — do not invent your own approach.**')
        if universal not in body:
            raise ValueError('Review changed upstream routing before updating Agent Reach')
        body = body.replace(universal, 'Use the relevant platform adapter within the ai_setup policy above.', 1)
        policy = (ROOT / 'config/AGENT_REACH.md').read_text(encoding='utf-8')
        (staged / 'SKILL.md').write_text('---\n' + yaml.safe_dump(meta, sort_keys=False) +
                                       '---\n\n' + policy + '\n' + body, encoding='utf-8')
        shutil.copy2(source / 'LICENSE', staged / 'LICENSE')
        shutil.copy2(ROOT / 'docs/AGENT_REACH.md', staged / 'references/ai-setup.md')
    target = i.home / '.agents/skills/agent-reach'
    i.copy_tree(source / 'agent_reach/skill', target, adapt)
    i.link(i.home / '.claude/skills/agent-reach', target)
    for path in (i.home / '.codex/AGENTS.md', i.home / '.claude/CLAUDE.md'):
        i.merge_text(path, (ROOT / 'config/AGENT_REACH.md').read_text(encoding='utf-8'), 'agentreach')


def check_python(i, python):
    expected = i.manifest['agent_reach']
    versions = json.loads(capture([python, '-B', '-c',
        'import json,importlib.metadata as m; print(json.dumps({n:m.version(n) for n in '
        '["agent-reach","yt-dlp","feedparser"]}))'], env=i.env, timeout=60))
    if versions != {'agent-reach': expected['version'], 'yt-dlp': expected['yt_dlp'],
                    'feedparser': expected['feedparser']}:
        raise ValueError('Agent Reach Python packages differ from the reviewed versions')
    help_text = capture([*command(i), '--help'], env=i.env, timeout=60)
    if 'doctor' not in help_text:
        raise ValueError('Agent Reach CLI failed to load')


def check_opencli(i, prefix):
    spec = i.manifest['agent_reach']['opencli']
    package = prefix / 'node_modules/@jackwener/opencli'
    data = json.loads((package / 'package.json').read_text(encoding='utf-8'))
    lock = json.loads((prefix / 'package-lock.json').read_text(encoding='utf-8'))
    if (data['name'] != '@jackwener/opencli' or data['version'] != spec['version'] or
            lock['packages']['node_modules/@jackwener/opencli']['integrity'] != spec['integrity']):
        raise ValueError('OpenCLI identity/integrity differs from the manifest')
    for name in ('dist/src/main.js', 'LICENSE', 'clis/facebook/search.js', 'clis/reddit/search.js'):
        if not (package / name).is_file():
            raise ValueError('OpenCLI is missing ' + name)
    node, _ = runtime_paths(i)
    argv = [node, package / 'dist/src/main.js']
    if capture([*argv, '--version'], env=dict(i.env, CI='1'), timeout=60) != spec['version']:
        raise ValueError('OpenCLI CLI version mismatch')
    return argv


def install(i):
    root, python, prefix = paths(i)
    # Reject edited runtime, launcher and skill paths before package changes.
    i.owned(root)
    i.owned(prefix)
    for name in ('agent-reach', 'agent-reach-python', 'agent-reach-yt-dlp', 'opencli'):
        i.owned(i.bin / (name + ('.cmd' if i.windows else '')))
    i.owned(i.home / '.agents/skills/agent-reach')
    source = i.fetch(i.spec('agent-reach'))
    project = tomllib.loads((source / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    spec = i.manifest['agent_reach']
    if project['name'] != 'agent-reach' or project['version'] != spec['version']:
        raise ValueError('Agent Reach source identity differs from the manifest')
    if not root.exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Create at the final path: pip's console-script shebangs must remain valid.
            run([sys.executable, '-m', 'venv', root], env=i.env, timeout=120)
            run([python, '-m', 'pip', 'install', '--no-cache-dir', '--disable-pip-version-check',
                 str(source), 'yt-dlp[default]==' + spec['yt_dlp'], 'feedparser==' + spec['feedparser']],
                env=i.env, timeout=600)
            check_python(i, python)
        except BaseException:
            shutil.rmtree(root)
            raise
        i.remember(root)
    check_python(i, python)
    if i.windows:
        from windows_runtime import ensure_node
        ensure_node(i, i.manifest['node'])
    else:
        import platform
        from runtime import ensure_node
        system = {'Darwin': 'darwin', 'Linux': 'linux'}[platform.system()]
        arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64'}[platform.machine()]
        ensure_node(i, i.manifest['node'], system, arch)
    node, npm = runtime_paths(i)
    if not prefix.exists():
        with tempfile.TemporaryDirectory(prefix='agent-reach-npm-', dir=prefix.parent) as tmp:
            staged = Path(tmp) / 'npm'
            run([node, npm, 'install', '--prefix', staged, '--ignore-scripts', '--no-bin-links',
                 '--no-audit', '--no-fund', '--registry=https://registry.npmjs.org',
                 '@jackwener/opencli@' + spec['opencli']['version']],
                env=dict(i.env, PATH=str(node.parent) + os.pathsep + i.env['PATH']), timeout=300)
            check_opencli(i, staged)
            staged.rename(prefix)
        i.remember(prefix)
    opencli = check_opencli(i, prefix)
    write_launcher(i, 'agent-reach', command(i), search_path=python.parent)
    write_launcher(i, 'agent-reach-python', [python, '-B'])
    write_launcher(i, 'agent-reach-yt-dlp', [python, '-B', '-m', 'yt_dlp'])
    write_launcher(i, 'opencli', opencli, ci=True)
    install_skill(i, source)
    i.state['agentreach'] = {'version': spec['version'], 'revision': i.spec('agent-reach')['revision'],
                             'opencli': spec['opencli']['version'], 'account_setup_by_installer': False,
                             'system_installer': False, 'hooks': False}
    i.save()
    verify(i)


def verify(i):
    root, python, prefix = paths(i)
    for path in (root, prefix, i.home / '.agents/skills/agent-reach'):
        i.owned(path)
        if not path.is_dir():
            raise ValueError('Missing Agent Reach installation path: ' + str(path))
    recorded = i.state.get('agentreach', {})
    if (recorded.get('version') != i.manifest['agent_reach']['version'] or
            recorded.get('revision') != i.spec('agent-reach')['revision'] or
            recorded.get('opencli') != i.manifest['agent_reach']['opencli']['version']):
        raise ValueError('Agent Reach state differs from the manifest; rerun --only agentreach')
    check_python(i, python)
    check_opencli(i, prefix)
    for name in ('agent-reach', 'agent-reach-python', 'agent-reach-yt-dlp', 'opencli'):
        path = i.bin / (name + ('.cmd' if i.windows else ''))
        i.owned(path)
        if not path.is_file():
            raise ValueError('Missing Agent Reach launcher: ' + str(path))
