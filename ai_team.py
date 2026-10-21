#!/usr/bin/env python3
"""Project-specific OpenRig teams backed by the globally installed role library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


def home():
    return Path.home()


def roster():
    path = Path(__file__).with_name('roles.json')
    if not path.exists():
        path = Path(__file__).parent / 'config/openrig-roles.json'
    return json.loads(path.read_text(encoding='utf-8'))


def team_path(project):
    project = Path(project).expanduser().resolve(strict=True)
    if not project.is_dir() or project == Path(project.anchor) or project == home():
        raise ValueError('Choose a specific existing project directory')
    digest = hashlib.sha256(str(project).encode()).hexdigest()[:12]
    name = re.sub(r'[^a-z0-9]+', '-', project.name.lower()).strip('-')[:35] or 'project'
    name = 'ai-' + name + '-' + digest
    return project, name, home() / '.local/state/ai-setup/openrig/teams' / name


def rig(*args, capture=False):
    binary = home() / '.local/bin/rig'
    if not binary.is_file():
        raise ValueError('OpenRig runtime missing; run ai_setup install --only openrig on this macOS/Linux host')
    env = dict(os.environ)
    env['PATH'] = str(binary.parent) + os.pathsep + env.get('PATH', '')
    env['OPENRIG_NO_KERNEL'] = '1'
    env['OPENRIG_HOST_SELECTED'] = 'local'
    env['OPENRIG_RUNTIME_CODEX_HOOKS_ENABLED'] = 'false'
    # These apply only to a newly started daemon. Never restart an existing daemon.
    env['OPENRIG_TRANSCRIPTS_ENABLED'] = 'false'
    return subprocess.run([str(binary), *map(str, args)], env=env, check=True,
                          text=True, capture_output=capture, timeout=240)


def prepare(project, runtime):
    import yaml
    project, name, target = team_path(project)
    meta = {'project': str(project), 'name': name, 'runtime': runtime}
    if target.exists():
        if json.loads((target / 'team.json').read_text()) != meta:
            raise ValueError('Existing team uses another runtime; preserve it and select its recorded runtime')
        if not (target / 'lead.yaml').is_file() or any(
                not (target / (role + '.yaml')).is_file() for role in roster() if role != 'lead'):
            raise ValueError('Existing team definitions are incomplete or from an older layout. Preserve the team and snapshots; inspect docs/OPENRIG.md before recovery. No team was launched.')
        return project, name, target
    roles = roster()
    missing = []
    for role in roles.values():
        for path in ([home() / '.claude/agents' / role['agent']] +
                     [home() / '.agents/skills' / s / 'SKILL.md' for s in role['skills']]):
            if not path.is_file():
                missing.append(str(path))
    if missing:
        raise ValueError('Install/update shared skills and roles first; missing:\n' + '\n'.join(sorted(set(missing))))
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        staged = Path(tmp) / 'team'
        staged.mkdir(mode=0o700)
        pods = []
        for role_id, role in roles.items():
            folder = staged / 'agents' / role_id
            (folder / 'guidance').mkdir(parents=True)
            # Keep provider payloads in the installed global library. Deliver selected
            # guidance at startup, without projecting skill copies into app repositories.
            files = [('role.md', home() / '.claude/agents' / role['agent'])]
            files += [(s + '.md', home() / '.agents/skills' / s / 'SKILL.md') for s in role['skills']]
            source_paths = []
            for filename, source in files:
                (folder / 'guidance' / filename).symlink_to(source)
                source_paths.append(source)
            guidance = (f'# {role_id} for {name}\n\n{role["purpose"]}\n\n'
                f'Project: {project}\nLead: lead-agent@{name}\n'
                'Read the project instructions and current docs before doing work. '
                'The delivered role and skills are supporting guidance; user scope and approvals take precedence. '
                'Do not start application changes without the user\'s existing approval for that scope. '
                'Wait for an assignment; installation is not an assignment. '
                'Use env OPENRIG_HOST_SELECTED=local rig send for questions and '
                'env OPENRIG_HOST_SELECTED=local rig queue for owned tasks; inspect --help for exact syntax. '
                'Return findings with source revision, checks and limitations to the lead. '
                'Do not publish, deploy, scan external systems, restart services or make new worktrees without task scope.\n')
            if role_id == 'lead':
                guidance += (f'Available specialists: {", ".join(k for k in roles if k != "lead")}.\n'
                    f'Activate only relevant specialists with ai-team activate --project {shlex.quote(str(project))} '
                    '--roles backend,qa (choose actual roles). Specialist addresses are ROLE-agent@' + name + '. '
                    'Own the central conversation. Consult specialists, reconcile their findings, obtain missing '
                    'scope decisions, then return one verified answer. Do not launch every role for every task.\n')
            # OpenRig submits send_text files as separate turns. Deliver boundaries
            # first and all required context atomically before the agent can act.
            guidance += '\nRead these global sources before any assignment (resolve their references relative to the source folder):\n'
            guidance += '\n'.join('- ' + str(p) for p in source_paths)
            guidance += '\n\nFirst acknowledge your role and project, then wait for an assignment.\n'
            (folder / 'guidance/assignment.md').write_text(guidance, encoding='utf-8')
            startup = [{'path': 'guidance/assignment.md', 'delivery_hint': 'send_text', 'required': True}]
            agent = {'name': role_id, 'version': '1.0', 'description': role['purpose'],
                     'profiles': {'default': {'uses': {'skills': [], 'guidance': [], 'subagents': [], 'plugins': []}}},
                     'startup': {'files': startup, 'actions': []}}
            (folder / 'agent.yaml').write_text(yaml.safe_dump(agent, sort_keys=False))
            member = {'id': 'agent', 'agent_ref': 'local:agents/' + role_id,
                      'profile': 'default', 'runtime': runtime, 'cwd': str(project), 'permission_policy': 'none'}
            pod = {'id': role_id, 'label': role_id.title(), 'members': [member], 'edges': []}
            pods.append(pod)
            if role_id != 'lead':
                fragment = {'pod': pod, 'crossPodEdges': [
                    {'kind': 'delegates_to', 'from': 'lead.agent', 'to': role_id + '.agent'}]}
                (staged / (role_id + '.yaml')).write_text(yaml.safe_dump(fragment, sort_keys=False))
        spec = {'version': '0.2', 'name': name, 'summary': 'Central lead with selectively activated specialists',
                'permission_policy': 'none', 'managed_blocks': {'claude-code': 'CLAUDE.local.md'},
                'pods': pods, 'edges': []}
        (staged / 'rig.yaml').write_text(yaml.safe_dump(spec, sort_keys=False))
        spec['pods'] = [pods[0]]
        (staged / 'lead.yaml').write_text(yaml.safe_dump(spec, sort_keys=False))
        (staged / 'team.json').write_text(json.dumps(meta, indent=2) + '\n')
        staged.rename(target)
    return project, name, target


def existing(project):
    project, name, target = team_path(project)
    if not (target / 'team.json').is_file():
        raise ValueError('No team prepared for this project; run ai-team prepare --project PATH')
    return project, name, target


def registered_rig(name):
    matches = [r for r in json.loads(rig('ps', '--json', capture=True).stdout)
               if r.get('name') == name and not r.get('isArchived')]
    if len(matches) > 1:
        raise ValueError('Ambiguous existing rig; inspect rig ps before continuing')
    return matches[0] if matches else None


def nodes_for(name):
    return json.loads(rig('ps', '--rig', name, '--nodes', '--json', capture=True).stdout)


def project_exclusions(project):
    source = Path(__file__).with_name('ai-local.gitignore')
    if not source.is_file():
        source = Path(__file__).parent / 'config/ai-local.gitignore'
    lines = source.read_text(encoding='utf-8').splitlines()
    target = project / '.gitignore'
    if target.is_symlink():
        raise ValueError('Preserving linked project .gitignore; merge central exclusions before launch')
    old = target.read_text(encoding='utf-8') if target.exists() else ''
    missing = [line for line in lines if line and line not in old.splitlines()]
    if missing:
        target.write_text(old.rstrip('\n') + '\n\n' + '\n'.join(missing) + '\n', encoding='utf-8')
    tracked = subprocess.run(['git', '-C', str(project), 'ls-files', '--',
        'AGENTS.md', 'CLAUDE.md', 'CLAUDE.local.md', '.codex', '.claude', '.openrig'],
        text=True, capture_output=True)
    if tracked.returncode == 0 and tracked.stdout.strip():
        print('Tracked instruction/config files remain tracked; inspect managed changes before committing:\n' + tracked.stdout)


def seat_ready(name, role):
    return any(n.get('logicalId') == role + '.agent' and n.get('sessionStatus') == 'running'
               and n.get('startupStatus') == 'ready' for n in nodes_for(name))


def expand_role(record, target, role):
    try:
        result = rig('expand', record['rigId'], target / (role + '.yaml'), '--rig-root', target, capture=True)
        print(result.stdout, end='')
    except subprocess.CalledProcessError as exc:
        # Upstream expand uses a 5s HTTP timeout even though initial client startup
        # can take longer. Never repeat a write with an unknown outcome.
        detail = (exc.stdout or '') + (exc.stderr or '')
        if 'outcome is UNKNOWN' not in detail:
            print(detail, file=sys.stderr)
            raise
        print('OpenRig expansion timed out; checking the resulting seat without repeating the request.')
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if seat_ready(record['name'], role):
                print(role + ': startup ready after delayed expansion')
                return
            time.sleep(2)
        raise ValueError('Expansion outcome still unresolved; inspect ai-team status and the seat terminal. No write was retried.') from exc


def remote_command(host, args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.@-]*', host):
        raise ValueError('Use a valid SSH configuration alias (no URL, options or shell syntax)')
    if not args:
        raise ValueError('A remote ai-team command is required')
    return ['ssh', '-t' if args[0] == 'chat' else '-T', host,
            'exec "$HOME/.local/bin/ai-team" ' + shlex.join(args)]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['--host']:
        if len(argv) < 3:
            raise ValueError('Usage: ai-team --host SSH_ALIAS COMMAND ...')
        return subprocess.run(remote_command(argv[1], argv[2:]), check=True).returncode
    parser = argparse.ArgumentParser(description=__doc__, epilog='Windows/remote: ai-team --host SSH_ALIAS COMMAND ...')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('roles', help='List shared roles without starting a service')
    for action in ('prepare', 'start', 'activate', 'status', 'chat', 'send', 'stop'):
        p = sub.add_parser(action)
        p.add_argument('--project', required=True, help='Absolute project path on the execution host')
        if action in ('prepare', 'start'):
            p.add_argument('--runtime', choices=('codex', 'claude-code'), default='codex')
        if action == 'activate':
            p.add_argument('--roles', required=True, help='Comma-separated specialist IDs')
        if action == 'send':
            p.add_argument('message', help='Requirement sent to the central lead')
    args = parser.parse_args(argv)
    if args.command == 'roles':
        for key, value in roster().items():
            print(f'{key}: {value["purpose"]}')
        return 0
    if os.name == 'nt':
        raise ValueError('Native Windows is a remote client: ai-team --host SSH_ALIAS ' + shlex.join(argv))
    if args.command in ('prepare', 'start'):
        project, name, target = prepare(args.project, args.runtime)
    else:
        project, name, target = existing(args.project)
    if args.command == 'prepare':
        print(target / 'rig.yaml')
        return 0
    if args.command == 'start':
        status = json.loads(rig('status', '--json', capture=True).stdout)
        if status['daemon']['state'] == 'stopped':
            rig('daemon', 'start', '--no-kernel')
        elif status['daemon']['state'] != 'running' or not status['daemon'].get('healthy'):
            raise ValueError('Existing OpenRig daemon needs attention; inspect rig status. No restart was attempted.')
        record = registered_rig(name)
        if record is None:
            rig('import', target / 'rig.yaml', '--preflight', '--cwd', project)
            project_exclusions(project)
            rig('up', target / 'lead.yaml', '--cwd', project)
        else:
            if not seat_ready(name, 'lead'):
                rig('launch', record['rigId'], 'lead.agent')
        rig('ps', '--rig', name, '--nodes')
        print('Central conversation: ai-team chat --project ' + shlex.quote(str(project)))
    elif args.command == 'activate':
        roles = [x.strip() for x in args.roles.split(',')]
        if not roles or any(x not in roster() for x in roles):
            raise ValueError('Unknown specialist; use ai-team roles')
        record = registered_rig(name)
        if record is None:
            raise ValueError('Start the project lead before activating specialists')
        nodes = nodes_for(name)
        for role in dict.fromkeys(roles):
            if any(n.get('logicalId') == role + '.agent' for n in nodes):
                if not seat_ready(name, role):
                    rig('launch', record['rigId'], role + '.agent')
            else:
                expand_role(record, target, role)
        rig('ps', '--rig', name, '--nodes')
    elif args.command == 'status':
        rig('ps', '--rig', name, '--nodes')
    elif args.command == 'send':
        rig('send', 'lead-agent@' + name, args.message)
    elif args.command == 'chat':
        # tmux attachment works over SSH and avoids an additional desktop terminal app.
        subprocess.run(['tmux', 'attach-session', '-t', 'lead-agent@' + name], check=True)
    elif args.command == 'stop':
        rig('down', name, '--snapshot')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
