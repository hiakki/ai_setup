"""Isolation/contract checks; opt in to the real npm/provider round trip."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

import dotagents_runtime as runtime
from setup import Installer


class DotagentsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.home = self.root / 'home with spaces'
        self.source = self.root / 'custom skills'
        self.skill = self.source / 'example'
        (self.skill / 'references').mkdir(parents=True)
        (self.skill / 'SKILL.md').write_text('---\nname: example\ndescription: Test reusable skill\n---\nRead references/details.md\n')
        (self.skill / 'references/details.md').write_text('Complete supporting reference\n')
        (self.skill / 'assets').mkdir()
        (self.skill / 'assets/sample.bin').write_bytes(bytes(range(256)))
        self.i = Installer(self.home, {'node': '24.14.0', 'dotagents': {'version': '3.1.0'}})
        self.prefix = self.home / '.local/share/ai-setup/dotagents'
        self.stage_home = self.prefix / 'staging-home'
        self.calls = []

    def provider(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if 'install' in args and '--prefix' in args:
            for name in ('dotagents', 'dotagents-lib'):
                package = self.prefix / 'node_modules/@sentry' / name
                package.mkdir(parents=True, exist_ok=True)
                (package / 'package.json').write_text(json.dumps({'version': '3.1.0'}))
        else:
            config = tomllib.loads((self.stage_home / '.agents/agents.toml').read_text())
            self.assertEqual(config['agents'], [])
            for entry in config['skills']:
                source = self.stage_home / '.agents' / entry['source'].removeprefix('path:')
                target = self.stage_home / '.agents/skills' / entry['name']
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(source, target)

    def stage(self, provider=None):
        with patch.object(runtime, 'node_and_npm', return_value=(Path('/node'), Path('/npm-cli.js'))), \
                patch.object(runtime, 'run', side_effect=provider or self.provider):
            return runtime.stage_custom(self.i, self.source)

    def test_complete_payload_repeat_install_and_actual_home_untouched(self):
        marker = self.home / '.agents/skills/personal/SKILL.md'
        marker.parent.mkdir(parents=True)
        marker.write_text('Private personal skill')
        for attempt in range(2):
            output = self.stage()
            self.assertEqual(runtime.skill_files(output / 'example'), runtime.skill_files(self.skill))
        self.assertEqual(marker.read_text(), 'Private personal skill')
        installs = [args for args, _ in self.calls if '--prefix' in args]
        self.assertEqual(len(installs), 1)
        self.assertIn('@sentry/dotagents@3.1.0', installs[0])
        self.assertIn('@sentry/dotagents-lib@3.1.0', installs[0])
        self.assertIn('--ignore-scripts', installs[0])

    def test_all_provider_home_overrides_are_isolated(self):
        self.i.env.update(DOTAGENTS_HOME='/do-not-write', DOTAGENTS_STATE_DIR='/do-not-write',
                          NODE_OPTIONS='--require=/private.js', CLAUDE_CONFIG_DIR='/do-not-write')
        self.stage()
        for _, kwargs in self.calls:
            env = kwargs['env']
            for key in ('HOME', 'USERPROFILE', 'CODEX_HOME', 'CLAUDE_CONFIG_DIR', 'APPDATA',
                        'LOCALAPPDATA', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_DATA_HOME',
                        'XDG_STATE_HOME', 'DOTAGENTS_HOME', 'DOTAGENTS_STATE_DIR', 'NPM_CONFIG_CACHE'):
                self.assertTrue(Path(env[key]).is_relative_to(self.stage_home), key)
            self.assertNotIn('NODE_OPTIONS', env)

    def test_provider_payload_loss_is_rejected(self):
        def omit_reference(args, **kwargs):
            self.provider(args, **kwargs)
            if '--global' in args:
                (self.stage_home / '.agents/skills/example/references/details.md').unlink()
        with self.assertRaisesRegex(ValueError, 'changed or omitted'):
            self.stage(omit_reference)
        self.assertNotIn('dotagents', self.i.state)

    def test_provider_failure_never_falls_back_to_source(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.stage(lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.CalledProcessError(1, 'dotagents')))
        self.assertNotIn('dotagents', self.i.state)

    def test_invalid_names_and_floating_versions_rejected(self):
        self.i.manifest['dotagents']['version'] = 'latest'
        with self.assertRaisesRegex(ValueError, 'exact stable version'):
            self.stage()
        self.i.manifest['dotagents']['version'] = '3.1.0'
        (self.skill / 'SKILL.md').write_text('---\nname: different\ndescription: mismatch\n---\n')
        with self.assertRaisesRegex(ValueError, 'does not match directory'):
            self.stage()
        self.assertFalse(self.calls)

    def test_windows_bootstrap_invokes_node_with_npm_javascript(self):
        self.i.windows = True
        node_root = self.home / 'managed node'
        with patch.object(runtime.shutil, 'which', return_value=None), \
                patch('windows_runtime.ensure_node', return_value=node_root) as ensure:
            node, npm = runtime.node_and_npm(self.i)
        self.assertEqual(node, node_root / 'node.exe')
        self.assertEqual(npm, node_root / 'node_modules/npm/bin/npm-cli.js')
        ensure.assert_called_once_with(self.i, '24.14.0')

    @unittest.skipIf(os.name == 'nt', 'Creating the malicious link requires Windows Developer Mode')
    def test_source_links_rejected_before_provider_invocation(self):
        (self.skill / 'references/private').symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, 'contains a link'):
            self.stage()
        self.assertFalse(self.calls)

    @unittest.skipIf(os.name == 'nt', 'Creating the malicious link requires Windows Developer Mode')
    def test_redirected_staging_output_rejected(self):
        self.stage()
        output = self.stage_home / '.agents/skills'
        shutil.rmtree(output)
        output.symlink_to(self.home / '.agents/skills')
        before = len(self.calls)
        with self.assertRaisesRegex(ValueError, 'linked dotagents staging path'):
            self.stage()
        self.assertEqual(len(self.calls), before)

    @unittest.skipUnless(os.environ.get('AI_SETUP_TEST_DOTAGENTS') == '1',
                         'Opt-in network test: AI_SETUP_TEST_DOTAGENTS=1')
    def test_real_provider_update_and_repeat(self):
        marker = self.home / '.codex/config.toml'
        marker.parent.mkdir(parents=True)
        marker.write_text('# Existing operator settings\n')
        for content in ('first version\n', 'updated version\n', 'updated version\n'):
            (self.skill / 'references/details.md').write_text(content)
            output = runtime.stage_custom(self.i, self.source)
            self.assertEqual(runtime.skill_files(output / 'example'), runtime.skill_files(self.skill))
            self.assertEqual(marker.read_text(), '# Existing operator settings\n')
        self.assertFalse((self.home / '.agents').exists())
        self.assertFalse((self.home / '.claude').exists())


if __name__ == '__main__':
    unittest.main()
