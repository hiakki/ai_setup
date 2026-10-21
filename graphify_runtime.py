"""Pinned Graphify CLI and skill without duplicate MCP servers or search hooks."""
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile
import tomllib

from setup import capture, run, venv_python


EXTRAS = ('pdf', 'office', 'sql', 'terraform')


def paths(installer):
    version = installer.manifest['graphify_version']
    root = installer.home / '.local/share/ai-setup' / ('graphify-' + version)
    python = venv_python(root)
    launcher = installer.bin / ('graphify.cmd' if installer.windows else 'graphify')
    return version, root, python, launcher


def package_version(source):
    document = tomllib.loads((source / 'pyproject.toml').read_text(encoding='utf-8'))
    project = document.get('project', {})
    if project.get('name') != 'graphifyy':
        raise ValueError('Graphify provider package name changed; review before updating')
    return project.get('version')


def check_cli(installer, command, version):
    actual = capture([*command, '--version'], env=installer.env, timeout=120)
    if not re.search(r'(?<![\d.])' + re.escape(version) + r'(?![\d.])', actual):
        raise ValueError(f'Graphify CLI does not report pinned version {version}')
    if not capture([*command, '--help'], env=installer.env, timeout=120):
        raise ValueError('Graphify CLI returned no help output')


def install_skill(installer, command):
    """Let the provider render its generic skill, then publish it through ai_setup."""
    target = installer.home / '.agents/skills/graphify'
    installer.owned(target)
    with tempfile.TemporaryDirectory(prefix='graphify-skill-', dir=installer.state_dir) as directory:
        stage_home = Path(directory) / 'home'
        env = dict(installer.env, HOME=str(stage_home), USERPROFILE=str(stage_home),
                   APPDATA=str(stage_home / 'AppData/Roaming'),
                   LOCALAPPDATA=str(stage_home / 'AppData/Local'))
        run([*command, 'install', '--platform', 'agents'], env=env)
        rendered = stage_home / '.agents/skills/graphify'
        if not (rendered / 'SKILL.md').is_file():
            raise ValueError('Graphify provider did not produce its generic Agent Skills package')
        installer.copy_tree(rendered, target)
    installer.link(installer.home / '.claude/skills/graphify', target)


def guidance(installer):
    note = (
        'Graphify is installed globally as an on-demand mixed-artifact graph tool. Use the '
        '`graphify` skill when a task needs relationships across source code and project-owned '
        'docs, ADRs, SQL schemas, configuration, PDFs or Office files. For ordinary code '
        'structure, callers and impact, prefer Codebase Memory and use Graft as the fallback. '
        'Do not install Graphify per project, register its MCP server, enable its search guards '
        'or commit `graphify-out/`. Its local code pass needs no model; semantic document work '
        'uses the active assistant unless the user explicitly authorizes another backend.'
    )
    for path in (installer.home / '.codex/AGENTS.md', installer.home / '.claude/CLAUDE.md'):
        installer.merge_text(path, note, 'graphify')


def install(installer):
    version, root, python, launcher = paths(installer)
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Graphify must use an exact provider version')
    source = installer.fetch(installer.spec('graphify'))
    if package_version(source) != version:
        raise ValueError('Graphify source revision does not match the pinned package version')
    installer.owned(root)
    installer.owned(launcher)
    if not root.exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='graphify-runtime-', dir=root.parent) as directory:
            staged = Path(directory) / 'venv'
            run([os.environ.get('PYTHON', sys.executable), '-m', 'venv', staged], env=installer.env)
            python = venv_python(staged)
            requirement = str(source) + '[' + ','.join(EXTRAS) + ']'
            run([python, '-m', 'pip', 'install', '--disable-pip-version-check', requirement],
                env=installer.env)
            candidate = [venv_python(staged), '-m', 'graphify']
            check_cli(installer, candidate, version)
            staged.rename(root)
        installer.remember(root)
    python = venv_python(root)
    command = [python, '-m', 'graphify']
    check_cli(installer, command, version)
    if installer.windows:
        from windows_runtime import launcher as windows_launcher
        installer.write(launcher, windows_launcher(command), 0o755)
    else:
        installer.write(launcher, '#!/bin/sh\nexec ' + shlex.quote(str(python)) +
                        ' -m graphify "$@"\n', 0o755)
    install_skill(installer, command)
    guidance(installer)
    installer.state['graphify'] = {
        'version': version,
        'revision': installer.spec('graphify')['revision'],
        'extras': list(EXTRAS),
        'mcp': False,
        'hooks': False,
    }
    installer.save()
    verify(installer)


def verify(installer):
    version, root, python, launcher = paths(installer)
    expected = {
        'version': version,
        'revision': installer.spec('graphify')['revision'],
        'extras': list(EXTRAS),
        'mcp': False,
        'hooks': False,
    }
    if installer.state.get('graphify') != expected:
        raise ValueError('Graphify installation differs from the manifest; rerun the graphify component')
    installer.owned(root)
    installer.owned(launcher)
    installer.owned(installer.home / '.agents/skills/graphify')
    if not launcher.is_file() or not python.is_file():
        raise ValueError('Graphify CLI is missing; rerun the graphify component')
    check_cli(installer, [python, '-m', 'graphify'], version)
