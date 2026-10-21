"""Full-machine sync is distinct from the lighter shared-content update."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from setup import DEFAULT_COMPONENTS, Installer, ROOT
import setup
from hub import Hub


class SyncTests(unittest.TestCase):
    def test_default_setup_selects_configured_hindsight_without_expanding_explicit_scope(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch('agentwiki_runtime.connection', return_value=None):
            env = {'HINDSIGHT_MCP_URL': 'https://memory.example.invalid/mcp/shared-learning/'}
            chosen = setup.add_configured_components('all', list(DEFAULT_COMPONENTS), Path(tmp), {}, env)
            self.assertIn('hindsight', chosen)
            self.assertEqual(setup.add_configured_components('custom', ['custom'], Path(tmp), {}, env), ['custom'])

    def test_default_sync_adds_new_defaults_and_keeps_optional_selection(self):
        selected = setup.select_sync_components('all', ['custom', 'hindsight', 'strix'])
        self.assertTrue(set(DEFAULT_COMPONENTS).issubset(selected))
        self.assertIn('hindsight', selected)
        self.assertIn('strix', selected)
        self.assertNotIn('skillui', selected)
        self.assertEqual(setup.select_sync_components('custom,docs', ['strix']), ['custom', 'docs'])

    def test_sync_plan_is_read_only_and_reports_retained_optional_components(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            state = home / '.local/state/ai-setup/state.json'
            state.parent.mkdir(parents=True)
            original = json.dumps({'completed': ['custom', 'strix'], 'files': {}, 'sources': {}})
            state.write_text(original)
            result = subprocess.run([sys.executable, str(ROOT / 'setup.py'), 'plan',
                '--sync', '--home', str(home)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('openrig', result.stdout)
            self.assertIn('strix', result.stdout.split('Components:')[1].splitlines()[0])
            self.assertEqual(state.read_text(), original)

    def test_failed_sync_never_records_verified_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            with patch.object(sys, 'argv', ['setup.py', 'sync', '--home', str(home), '--only', 'custom']), \
                    patch.object(Installer, 'custom', side_effect=ValueError('fixture failure')):
                with self.assertRaisesRegex(ValueError, 'fixture failure'):
                    setup.main()
            state = json.loads((home / '.local/state/ai-setup/state.json').read_text())
            self.assertEqual(state['last_operation']['status'], 'incomplete')
            self.assertNotIn('last_sync', state)

    def test_hub_sync_uses_native_launcher_and_does_not_claim_content_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / 'home'
            checkout = Path(tmp) / 'source'
            checkout.mkdir()
            (checkout / 'install.sh').touch()
            (checkout / 'install.ps1').touch()
            hub = Hub(home)
            hub.state_file.parent.mkdir(parents=True)
            hub.state_file.write_text(json.dumps({'completed': ['custom'], 'files': {}}))
            for windows in (False, True):
                with self.subTest(windows=windows), patch('hub.sys.platform', 'win32' if windows else 'darwin'), \
                        patch.object(hub, 'checkout', return_value=(checkout, 'abc')), \
                        patch('hub.run') as run:
                    hub.sync('fixture', 'main', 'custom')
                args = list(map(str, run.call_args.args[0]))
                self.assertIn(str(checkout / ('install.ps1' if windows else 'install.sh')), args)
                self.assertIn('sync', args)
                self.assertIn(str(home.resolve()), args)
            self.assertFalse(hub.history.exists())

    def test_hub_sync_preserves_local_edits_before_fetch_or_bootstrap(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Hub(Path(tmp))
            hub.state_file.parent.mkdir(parents=True)
            (hub.home / 'managed.txt').write_text('personal improvement')
            hub.state_file.write_text(json.dumps({'files': {'managed.txt': 'previous'}}))
            with patch.object(hub, 'checkout') as fetch, patch('hub.run') as run:
                with self.assertRaisesRegex(ValueError, 'local edits'):
                    hub.sync('fixture', 'main')
            fetch.assert_not_called()
            run.assert_not_called()
            self.assertEqual((hub.home / 'managed.txt').read_text(), 'personal improvement')


if __name__ == '__main__':
    unittest.main()
