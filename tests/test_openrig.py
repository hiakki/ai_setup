import json
import os
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ai_team
from setup import Installer, ROOT, select_components
from openrig_runtime import install, locations, ensure_linux_prerequisites


class OpenRigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home with spaces'
        self.home.mkdir()
        p = patch('ai_team.home', return_value=self.home)
        p.start()
        self.addCleanup(p.stop)

    def populate(self):
        for role in ai_team.roster().values():
            paths = [self.home / '.claude/agents' / role['agent']]
            paths += [self.home / '.agents/skills' / s / 'SKILL.md' for s in role['skills']]
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('# Test shared guidance\n')

    def test_default_and_selective_dispatch(self):
        self.assertIn('openrig', select_components('all'))
        self.assertEqual(select_components('openrig'), ['openrig'])

    def test_minimal_linux_installs_native_build_prerequisites_once(self):
        i = Installer(self.home, json.loads((ROOT / 'manifest.json').read_text()))
        def available(command, **kwargs):
            return None if command in ('make', 'g++', 'ps') else '/usr/bin/' + command
        with patch('openrig_runtime.platform.system', return_value='Linux'), \
                patch('openrig_runtime.shutil.which', side_effect=available), \
                patch('openrig_runtime.os.geteuid', return_value=0, create=True), \
                patch('openrig_runtime.run') as run:
            ensure_linux_prerequisites(i)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0],
            ['apt-get', 'install', '-y', '--no-install-recommends', 'build-essential', 'procps'])
        with patch('openrig_runtime.platform.system', return_value='Linux'), \
                patch('openrig_runtime.shutil.which', return_value='/usr/bin/tool'), \
                patch('openrig_runtime.run') as run:
            ensure_linux_prerequisites(i)
        run.assert_not_called()

    @unittest.skipIf(os.name == 'nt', 'Project execution is on the macOS/Linux SSH host')
    def test_project_rosters_are_isolated_idempotent_and_do_not_write_app(self):
        self.populate()
        a, b = self.home / 'first app', self.home / 'second app'
        a.mkdir()
        b.mkdir()
        first, second = ai_team.prepare(a, 'codex'), ai_team.prepare(b, 'claude-code')
        self.assertNotEqual(first[1], second[1])
        self.assertEqual(first, ai_team.prepare(a, 'codex'))
        self.assertEqual(list(a.iterdir()), [])
        spec = yaml.safe_load((first[2] / 'rig.yaml').read_text())
        self.assertEqual(len(spec['pods']), 14)
        self.assertEqual(spec['permission_policy'], 'none')
        self.assertNotIn('services', spec)
        for member in [p['members'][0] for p in spec['pods']]:
            folder = first[2] / member['agent_ref'][6:]
            agent = yaml.safe_load((folder / 'agent.yaml').read_text())
            self.assertEqual(len(agent['startup']['files']), 1)
            for startup in agent['startup']['files']:
                self.assertTrue((folder / startup['path']).is_file())
            self.assertFalse(agent['profiles']['default']['uses']['skills'])
        with self.assertRaisesRegex(ValueError, 'another runtime'):
            ai_team.prepare(a, 'claude-code')

    def test_missing_skill_prevents_partial_team(self):
        self.populate()
        (self.home / '.agents/skills/build-usable-apps/SKILL.md').unlink()
        project = self.home / 'app'
        project.mkdir()
        with self.assertRaisesRegex(ValueError, 'build-usable-apps'):
            ai_team.prepare(project, 'codex')
        self.assertFalse(ai_team.team_path(project)[2].exists())

    def test_remote_arguments_remain_literal(self):
        args = ['send', '--project', '/srv/app with spaces', 'literal $(touch bad); `bad` "text"']
        cmd = ai_team.remote_command('user@dev-host', args)
        self.assertEqual(cmd[:3], ['ssh', '-T', 'user@dev-host'])
        self.assertEqual(shlex.split(cmd[3])[2:], args)
        for host in ('-oProxyCommand=bad', 'host;bad', 'host\nother', 'https://host'):
            with self.assertRaises(ValueError):
                ai_team.remote_command(host, args)

    def test_unmanaged_launcher_preserved(self):
        i = Installer(self.home, json.loads((ROOT / 'manifest.json').read_text()))
        i.bin.mkdir(parents=True)
        name = 'ai-team.cmd' if i.windows else 'ai-team'
        (i.bin / name).write_text('my launcher')
        with self.assertRaisesRegex(ValueError, 'Preserving unmanaged'):
            install(i)
        self.assertEqual((i.bin / name).read_text(), 'my launcher')

    def test_windows_install_only_remote_entrypoint(self):
        i = Installer(self.home, json.loads((ROOT / 'manifest.json').read_text()))
        i.windows = True
        with patch.object(i, 'link'), patch('openrig_runtime.verify'), patch('openrig_runtime.run') as run:
            install(i)
        run.assert_not_called()
        self.assertEqual(i.state['openrig']['mode'], 'ssh-client')
        self.assertTrue((i.bin / 'ai-team.cmd').is_file())
        self.assertFalse(locations(i)[0].exists())
        self.assertFalse((self.home / '.codex/config.toml').exists())
        self.assertFalse((self.home / '.claude.json').exists())

    def test_local_routing_overrides_remote_selection_without_config_edits(self):
        binary = self.home / '.local/bin/rig'
        binary.parent.mkdir(parents=True)
        binary.touch()
        with patch.dict('os.environ', {'OPENRIG_HOST_SELECTED': 'wrong-remote'}), patch('ai_team.subprocess.run') as run:
            ai_team.rig('ps')
        self.assertEqual(run.call_args.kwargs['env']['OPENRIG_HOST_SELECTED'], 'local')

    def test_expansion_timeout_is_reconciled_without_duplicate_write(self):
        import subprocess
        error = subprocess.CalledProcessError(1, ['rig', 'expand'], stderr='outcome is UNKNOWN')
        with patch('ai_team.rig', side_effect=error) as run, patch('ai_team.seat_ready', return_value=True):
            ai_team.expand_role({'rigId': 'id', 'name': 'test'}, self.home, 'qa')
        self.assertEqual(run.call_count, 1)

    def test_expansion_failure_is_not_reported_as_success(self):
        import subprocess
        error = subprocess.CalledProcessError(1, ['rig', 'expand'], stderr='invalid profile')
        with patch('ai_team.rig', side_effect=error), patch('ai_team.seat_ready') as ready:
            with self.assertRaises(subprocess.CalledProcessError):
                ai_team.expand_role({'rigId': 'id', 'name': 'test'}, self.home, 'qa')
        ready.assert_not_called()

    def test_ignore_merge_preserves_existing_rules(self):
        project = self.home / 'project'
        project.mkdir()
        path = project / '.gitignore'
        path.write_text('node_modules/\n# custom rule\n')
        ai_team.project_exclusions(project)
        first = path.read_text()
        ai_team.project_exclusions(project)
        self.assertEqual(path.read_text(), first)
        self.assertTrue(first.startswith('node_modules/\n# custom rule\n'))
        for line in (ROOT / 'config/ai-local.gitignore').read_text().splitlines():
            if line:
                self.assertIn(line, first.splitlines())


if __name__ == '__main__':
    unittest.main()
