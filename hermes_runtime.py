"""Hermes integration, using its pinned, unmodified upstream installer."""
import os
from pathlib import Path

import yaml

from setup import ROOT, capture, is_link, run

STAGES = ('prerequisites', 'venv', 'python-deps', 'config', 'products', 'complete')


def data_home(installer):
    if installer.windows:
        return Path(installer.env['LOCALAPPDATA']) / 'hermes'
    return installer.home / '.hermes'


def stage_command(installer, source, stage):
    home = data_home(installer)
    if installer.windows:
        return ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                source / 'scripts/install.ps1', '-InstallDir', source, '-HermesHome', home,
                '-Commit', installer.spec('hermes-agent')['revision'],
                '-NonInteractive', '-SkipBrowser', '-Stage', stage]
    return ['bash', source / 'scripts/install.sh', '--dir', source,
            '--hermes-home', home, '--commit', installer.spec('hermes-agent')['revision'],
            '--non-interactive', '--skip-browser', '--stage', stage]


def launcher(installer):
    if installer.windows:
        binary = data_home(installer) / 'bin/hermes.exe'
        return binary if binary.exists() else binary.with_suffix('.cmd')
    return installer.bin / 'hermes'


def read_config(path):
    config = yaml.safe_load(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    if config is None:
        config = {}
    if not isinstance(config, dict):
        raise ValueError(f'Expected a mapping in {path}; preserving existing configuration')
    skills = config.get('skills', {})
    if not isinstance(skills, dict):
        raise ValueError(f'Expected skills mapping in {path}')
    external = skills.get('external_dirs', [])
    if not isinstance(external, list) or not all(isinstance(p, str) for p in external):
        raise ValueError(f'Expected skills.external_dirs list of paths in {path}')
    return config, skills, external


def configure_skills(installer):
    path = data_home(installer) / 'config.yaml'
    installer.safe(path)
    if is_link(path):
        raise ValueError(f'Preserving linked Hermes configuration: {path}')
    config, skills, external = read_config(path)
    shared = str(installer.home / '.agents/skills')
    # Preserve explicit creation targets and all unrelated operator settings.
    if shared in external:
        return
    skills['external_dirs'] = [*external, shared]
    config['skills'] = skills
    installer.backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('config.yaml.ai-setup-tmp')
    temporary.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding='utf-8')
    temporary.chmod(0o600)
    temporary.replace(path)


def verify(installer):
    source = installer.sources / 'hermes-agent'
    spec = installer.spec('hermes-agent')
    if capture(['git', '-C', source, 'rev-parse', 'HEAD']) != spec['revision']:
        raise ValueError('Hermes source revision differs from manifest; review the update before adopting it')
    if capture(['git', '-C', source, 'remote', 'get-url', 'origin']) != spec['url']:
        raise ValueError('Hermes source origin differs from manifest')
    if capture(['git', '-C', source, 'diff', '--name-only', 'HEAD']):
        raise ValueError('Hermes provider source contains local edits')
    _, _, external = read_config(data_home(installer) / 'config.yaml')
    if str(installer.home / '.agents/skills') not in external:
        raise ValueError('Hermes shared skills configuration is missing; rerun --only hermes')
    if not launcher(installer).is_file():
        raise ValueError('Hermes launcher is missing; rerun --only hermes')


def install_guidance(installer):
    installer.install_skill(ROOT / 'custom', {'name': 'hermes-workflows', 'path': 'skills/hermes-workflows'})
    note = ('Hermes is installed for this user. For persistent-agent tasks, read '
            '`~/.agents/skills/hermes-workflows/SKILL.md`. Run `hermes --help` before invoking it. '
            'Installation does not authorize scheduled jobs, messaging or external changes. '
            'Keep learned skills in Hermes and review before promoting them to shared sources.')
    for path in (installer.home / '.codex/AGENTS.md', installer.home / '.claude/CLAUDE.md'):
        installer.merge_text(path, note, 'hermes')


def install(installer):
    # The provider's Windows products stage publishes the current user's PATH.
    # Reject alternate test homes before any mutation of that real user's registry.
    if installer.windows and installer.home != Path(os.environ['USERPROFILE']).resolve():
        raise ValueError('Hermes on Windows must be installed for the current user; omit --home/-HomeDirectory')
    home = data_home(installer)
    installer.safe(home / 'config.yaml')
    if is_link(home) or is_link(home / 'config.yaml'):
        raise ValueError(f'Preserving linked Hermes home/configuration: {home}')
    read_config(home / 'config.yaml')  # Fail early on malformed operator configuration.
    if installer.windows:
        for name in ('hermes.exe', 'hermes.cmd'):
            installer.owned(home / 'bin' / name)
    else:
        installer.owned(launcher(installer))
    skill = installer.home / '.agents/skills/hermes-workflows'
    installer.owned(skill)
    # No provider tree, Python environment or browser is vendored in ai_setup.
    source = installer.fetch(installer.spec('hermes-agent'))
    env = dict(installer.env)
    for key in tuple(env):
        if key.startswith('HERMES_'):
            env.pop(key)
    env['HERMES_HOME'] = str(home)
    env.setdefault('UV_HTTP_TIMEOUT', '300')
    for stage in STAGES:
        # Repository checkout is handled by fetch(): the provider's repository
        # stage updates main and may stash/reset; never invoke it on our pin.
        try:
            run(stage_command(installer, source, stage), env=env, cwd=source)
        finally:
            # A build can fail after publishing the launcher. Record our partial
            # output so retry does not misclassify it as an unrelated install.
            if stage == 'products' and launcher(installer).is_file():
                installer.remember(launcher(installer))
    configure_skills(installer)
    install_guidance(installer)
    verify(installer)
    run([launcher(installer), '--help'], env=env, cwd=home)
    print('Hermes CLI installed. Run hermes model to connect your provider. '
          'Gateway, schedules, desktop and browser downloads were not enabled.')
