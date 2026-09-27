"""Real Git distribution, contribution and rollback through the shared installer."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hub import Hub, fingerprint, operation_lock, HELD_LOCKS


class HubTests(unittest.TestCase):
    def setUp(self):
        work = ROOT / '.work'
        work.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=work)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'central source'
        self.source.mkdir()
        for name in ('setup.py', 'runtime.py', 'hub.py', 'library.py'):
            shutil.copy2(ROOT / name, self.source / name)
        for name in ('custom/skills/example', 'docs', 'config'):
            (self.source / name).mkdir(parents=True)
        (self.source / 'README.md').write_text('# Central docs\n')
        (self.source / 'docs/guide.md').write_text('# Version one\n')
        (self.source / 'config/example.md').write_text('Shared configuration reference\n')
        (self.source / 'manifest.json').write_text(json.dumps({'schema': 1, 'sources': []}))
        self.skill = self.source / 'custom/skills/example/SKILL.md'
        self.skill.write_text('---\nname: example\ndescription: A reusable example\n---\nVersion one\n')
        self.git('init', '-q', '-b', 'main')
        self.commit('Initial source')
        self.home = self.root / 'first user'
        self.setup(self.source, self.home, 'install')
        self.hub = Hub(self.home)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], text=True).strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def setup(self, source, home, command):
        result = subprocess.run([sys.executable, str(source / 'setup.py'), command,
                                 '--home', str(home), '--only', 'custom,docs,hub'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def revise(self):
        self.skill.write_text(self.skill.read_text().replace('Version one', 'Version two'))
        (self.source / 'docs/guide.md').write_text('# Version two\n')
        return self.commit('Improve shared skill and docs')

    def test_two_machines_receive_same_revision_and_rollback(self):
        second = self.root / 'second user'
        self.setup(self.source, second, 'install')
        old = fingerprint(self.home / '.agents/skills/example')
        revision = self.revise()
        for home in (self.home, second):
            Hub(home).update(str(self.source), 'main')
            self.assertIn('Version two', (home / '.agents/skills/example/SKILL.md').read_text())
            self.assertIn('Version two', (home / '.local/share/ai-setup/docs/docs/guide.md').read_text())
            self.assertEqual(Hub(home).state()['hub']['revision'], revision)
        self.assertEqual(fingerprint(self.home / '.agents/skills/example'), fingerprint(second / '.agents/skills/example'))
        self.hub.rollback()
        self.assertEqual(fingerprint(self.home / '.agents/skills/example'), old)
        self.assertIn('Version one', (self.home / '.local/share/ai-setup/docs/docs/guide.md').read_text())
        self.assertIn('Version two', (second / '.agents/skills/example/SKILL.md').read_text())
        self.setup(self.source, self.home, 'verify')

    def test_update_preserves_local_edits_and_failed_snapshot_can_restore_state(self):
        local = self.home / '.agents/skills/example/SKILL.md'
        local.write_text(local.read_text() + '\nLocal improvement\n')
        self.revise()
        with self.assertRaises(subprocess.CalledProcessError):
            self.hub.update(str(self.source), 'main')
        self.assertIn('Local improvement', local.read_text())
        self.hub.rollback()
        self.assertIn('Local improvement', local.read_text())

    def test_rollback_refuses_edits_after_update(self):
        self.revise()
        self.hub.update(str(self.source), 'main')
        local = self.home / '.agents/skills/example/SKILL.md'
        local.write_text(local.read_text() + '\nNew local change\n')
        with self.assertRaisesRegex(ValueError, 'Preserving edits'):
            self.hub.rollback()
        self.assertIn('New local change', local.read_text())

    def test_contribution_is_reviewable_without_committing(self):
        before = self.git('rev-parse', 'HEAD')
        local = self.home / '.agents/skills/example/SKILL.md'
        local.write_text(local.read_text() + '\nReusable improvement\n')
        self.hub.contribute('example', self.source)
        self.assertEqual(local.read_bytes(), self.skill.read_bytes())
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertIn('custom/skills/example/SKILL.md', self.git('status', '--porcelain'))

    def test_contribution_preserves_independent_source_edits(self):
        local = self.home / '.agents/skills/example/SKILL.md'
        local.write_text(local.read_text() + '\nLocal change\n')
        self.skill.write_text(self.skill.read_text() + '\nIndependent source change\n')
        with self.assertRaisesRegex(ValueError, 'independent edits'):
            self.hub.contribute('example', self.source)
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.hub.contribute('third-party', self.source)
        with self.assertRaisesRegex(ValueError, 'Invalid skill'):
            self.hub.contribute('../escape', self.source)

    def test_invalid_revision_or_runtime_selection_does_not_mutate_installation(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.hub.update(str(self.source), 'missing-ref')
        self.assertEqual(fingerprint(self.home / '.agents/skills/example'),
                         fingerprint(self.source / 'custom/skills/example'))
        with self.assertRaisesRegex(ValueError, 'only shared'):
            self.hub.update(str(self.source), 'main', 'runtime')
        with self.assertRaisesRegex(ValueError, 'Invalid Git'):
            self.hub.update(str(self.source), '--upload-pack=evil')

    def test_shared_lock_blocks_direct_install_and_allows_owned_child(self):
        command = [sys.executable, str(self.source / 'setup.py'), 'update',
                   '--home', str(self.home), '--only', 'custom']
        with operation_lock(self.home):
            denied = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(denied.returncode, 0)
            denied = subprocess.run(command, text=True, capture_output=True,
                                    env=dict(os.environ, AI_SETUP_HUB_LOCK_TOKEN='wrong'))
            self.assertNotEqual(denied.returncode, 0)
            allowed = subprocess.run(command, text=True, capture_output=True,
                                     env=dict(os.environ, AI_SETUP_HUB_LOCK_TOKEN=HELD_LOCKS[self.home.resolve()]))
            self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
        allowed = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)

    def test_snapshot_excludes_unrelated_runtime_and_keeps_existing_personal_notes(self):
        state = self.hub.state()
        state['files']['.local/share/large-runtime'] = 'fixture'
        paths = self.hub.snapshot_paths(state, self.source, ['custom'])
        self.assertNotIn('.local/share/large-runtime', paths)
        self.assertIn('.agents/skills/example', paths)
        self.assertIn('.claude/skills/example', paths)

    def test_authored_agents_install_both_client_adapters(self):
        folder = self.source / 'custom/agents'
        folder.mkdir()
        (folder / 'README.md').write_text('This is not a role.\n')
        (folder / 'shared-reviewer.md').write_text('---\nname: Shared Reviewer\ndescription: Review central changes\n---\nInspect actual evidence.\n')
        result = subprocess.run([sys.executable, str(self.source / 'setup.py'), 'install',
                                 '--home', str(self.home), '--only', 'agents'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ('.claude/agents/shared-reviewer.md', '.codex/agents/shared-reviewer.toml'):
            self.assertIn('Inspect actual evidence.', (self.home / name).read_text())
        self.assertFalse((self.home / '.claude/agents/readme.md').exists())

    def test_rollback_preserves_independent_installer_state(self):
        self.revise()
        self.hub.update(str(self.source), 'main')
        state = self.hub.state()
        state['completed'].append('independent-component')
        self.hub.state_file.write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError, 'state changed'):
            self.hub.rollback()


if __name__ == '__main__':
    unittest.main()
