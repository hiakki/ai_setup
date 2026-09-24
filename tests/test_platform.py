"""Exercise shared installer behavior required by native Windows."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PlatformTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)

    @unittest.skipUnless(os.name == 'nt', 'Requires native Windows batch invocation')
    def test_batch_command_preserves_quoted_path_and_literal_arguments(self):
        from setup import capture
        with tempfile.TemporaryDirectory(prefix='batch & spaces ', dir=ROOT / '.work') as temp:
            folder = Path(temp)
            program = folder / 'arguments.py'
            program.write_text('import json, sys\nprint(json.dumps(sys.argv[1:]))\n', encoding='utf-8')
            shim = folder / 'npx.cmd'
            shim.write_text('@echo off\nsetlocal DisableDelayedExpansion\n'
                            f'"{sys.executable}" "{program}" %*\n', encoding='utf-8')
            arguments = ['-y', '@playwright/mcp@latest', '--browser', 'chrome',
                         'space here', 'literal & (parentheses) | < > ^ !', '']
            self.assertEqual(json.loads(capture([shim, *arguments])), arguments)

    def test_import_and_plan_without_unix_fcntl(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as temp:
            result = subprocess.run([sys.executable, '-c',
                "import sys; sys.modules['fcntl'] = None; import setup; "
                "sys.argv = ['setup.py', 'plan', '--home', sys.argv[1]]; setup.main()", temp],
                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Components:', result.stdout)

    def test_browser_download_child_gets_longer_timeout_without_changing_parent(self):
        from unittest.mock import patch
        from setup import Installer, capture
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as temp:
            with patch.dict(os.environ):
                os.environ.pop('PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT', None)
                installer = Installer(Path(temp), {})
                received = capture([sys.executable, '-c',
                    "import os; print(os.environ.get('PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT', '30000'))"],
                    env=installer.env)
                self.assertGreaterEqual(int(received), 300000)
                self.assertNotIn('PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT', os.environ)

    def test_browser_download_respects_operator_timeout(self):
        from unittest.mock import patch
        from setup import Installer, capture
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as temp:
            with patch.dict(os.environ, {'PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT': '600000'}):
                installer = Installer(Path(temp), {})
                received = capture([sys.executable, '-c',
                    "import os; print(os.environ['PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT'])"],
                    env=installer.env)
                self.assertEqual(received, '600000')

    def test_windows_browser_cache_matches_fresh_terminal_and_isolates_test_home(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from setup import Installer
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as temp:
            home = Path(temp) / 'user'
            local = home / 'redirected-app-data'
            environment = {'USERPROFILE': str(home), 'LOCALAPPDATA': str(local)}
            with patch('setup.os', SimpleNamespace(name='nt', environ=environment, pathsep=';')):
                installed = Installer(home, {})
                self.assertEqual(installed.env['PLAYWRIGHT_BROWSERS_PATH'], str(local / 'ms-playwright'))
                environment['PLAYWRIGHT_BROWSERS_PATH'] = str(home / 'chosen-browser-cache')
                self.assertEqual(Installer(home, {}).env['PLAYWRIGHT_BROWSERS_PATH'], environment['PLAYWRIGHT_BROWSERS_PATH'])
                isolated = Installer(home / 'test-home', {})
                self.assertEqual(isolated.env['PLAYWRIGHT_BROWSERS_PATH'], str(home / 'test-home/AppData/Local/ms-playwright'))

    def test_lock_excludes_another_process_and_releases_on_exit(self):
        import setup
        self.assertTrue(hasattr(setup, 'install_lock'), 'Cross-platform installation lock missing')
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as temp:
            path = Path(temp) / 'install.lock'
            code = ('from pathlib import Path; from setup import install_lock; '
                    'import sys;\nwith install_lock(Path(sys.argv[1])): print("acquired")')
            with setup.install_lock(path):
                blocked = subprocess.run([sys.executable, '-c', code, str(path)],
                                         cwd=ROOT, text=True, capture_output=True)
                self.assertNotEqual(blocked.returncode, 0)
                self.assertNotIn('acquired', blocked.stdout)
            released = subprocess.run([sys.executable, '-c', code, str(path)],
                                      cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(released.returncode, 0, released.stderr)
            self.assertIn('acquired', released.stdout)

    @unittest.skipUnless(os.name == 'nt', 'Native junction semantics require Windows')
    def test_directory_links_work_without_developer_mode(self):
        from setup import Installer, fingerprint, is_link
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as temp:
            home = Path(temp) / 'User & Spaces'
            source = home / '.agents/skills/example'
            source.mkdir(parents=True)
            (source / 'SKILL.md').write_text('UTF-8 skill: café ✓', encoding='utf-8')
            i = Installer(home, {'schema': 1, 'sources': [], 'npm': {}})
            target = home / '.claude/skills/example'
            i.link(target, source)
            self.assertTrue(is_link(target))
            self.assertEqual(target.resolve(), source.resolve())
            self.assertEqual((target / 'SKILL.md').read_text(encoding='utf-8'), 'UTF-8 skill: café ✓')
            before = fingerprint(target)
            i.link(target, source)
            self.assertEqual(fingerprint(target), before)
            i.verify()


if __name__ == '__main__':
    unittest.main()
