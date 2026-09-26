import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT
import skillui_runtime as skillui


class SkillUITests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name) / 'home with spaces'
        self.i = Installer(self.home, {'node': '24.20.0', 'optional_npm': {'skillui': '1.3.4'}})
        self.calls = []

    def fake_run(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        if 'install' in argv:
            prefix = Path(argv[argv.index('--prefix') + 1])
            root = skillui.package_root(self.i, prefix)
            (root / 'dist').mkdir(parents=True)
            (root / 'package.json').write_text(json.dumps({'name': 'skillui', 'version': '1.3.4'}))
            (root / 'dist/cli.js').write_text('console.log("help")')

    def install(self):
        with patch.object(skillui, 'runtime_commands', return_value=(Path('/node with spaces/node'), ['npm'])), \
                patch.object(skillui, 'run', side_effect=self.fake_run):
            skillui.install(self.i)

    def test_install_rerun_preserves_instructions_and_skips_download(self):
        path = self.home / '.codex/AGENTS.md'
        path.parent.mkdir(parents=True)
        path.write_text('Operator instructions\n')
        self.install()
        first = path.read_bytes()
        self.install()
        self.assertEqual(first, path.read_bytes())
        installs = [(args, kw) for args, kw in self.calls if 'install' in args]
        self.assertEqual(len(installs), 1)
        args, kwargs = installs[0]
        self.assertIn('skillui@1.3.4', args)
        self.assertIn('--registry=https://registry.npmjs.org', args)
        self.assertEqual(kwargs['env']['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'], '1')
        self.assertNotIn('playwright', args)
        self.assertIn('Operator instructions', path.read_text())
        self.assertIn('skillui --dir', path.read_text())
        if not self.i.windows:
            self.assertIn('"$@"', (self.i.bin / 'skillui').read_text())

    def test_unmanaged_launcher_is_preserved_before_download(self):
        path = self.i.bin / ('skillui.cmd' if self.i.windows else 'skillui')
        path.parent.mkdir(parents=True)
        path.write_text('operator-owned')
        with self.assertRaisesRegex(ValueError, 'unmanaged'):
            self.install()
        self.assertEqual(self.calls, [])
        self.assertEqual(path.read_text(), 'operator-owned')

    def test_changed_package_is_preserved(self):
        self.install()
        prefix = self.home / '.local/share/ai-setup/skillui-1.3.4'
        path = skillui.package_root(self.i, prefix) / 'dist/cli.js'
        path.write_text('locally modified')
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            self.install()
        self.assertEqual(path.read_text(), 'locally modified')

    def test_native_windows_uses_native_node_entrypoint(self):
        self.i.windows = True
        self.install()
        launcher = (self.i.bin / 'skillui.cmd').read_text()
        self.assertIn('DisableDelayedExpansion', launcher)
        self.assertIn('"' + str(Path('/node with spaces/node')) + '"', launcher)
        self.assertIn(str(Path('node_modules/skillui/dist/cli.js')) + '" %*', launcher)
        self.assertNotIn('wsl', launcher)

    def test_missing_or_old_runtime_has_actionable_error(self):
        with patch.object(skillui.shutil, 'which', return_value=None):
            with self.assertRaisesRegex(ValueError, 'runtime component'):
                skillui.runtime_commands(self.i)
        with patch.object(skillui.shutil, 'which', return_value='/bin/node'), \
                patch.object(skillui, 'capture', return_value='v16.0.0'):
            with self.assertRaisesRegex(ValueError, 'Node.js 18'):
                skillui.runtime_commands(self.i)

    def test_failed_download_leaves_no_owned_partial_install(self):
        with patch.object(skillui, 'runtime_commands', return_value=(Path('/node'), ['npm'])), \
                patch.object(skillui, 'run', side_effect=RuntimeError('download failed')):
            with self.assertRaisesRegex(RuntimeError, 'download failed'):
                skillui.install(self.i)
        prefix = self.home / '.local/share/ai-setup/skillui-1.3.4'
        self.assertFalse(prefix.exists())
        self.assertEqual(list(prefix.parent.iterdir()), [])
        self.assertNotIn('skillui', self.i.state)


if __name__ == '__main__':
    unittest.main()
