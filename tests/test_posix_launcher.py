"""Exercise the Bash launcher with real plan validation and mocked host installers."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.name == 'nt', 'Bash launcher is for macOS/Linux')
class PosixLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.bin = self.directory / 'bin'
        self.bin.mkdir()
        self.home = self.directory / 'home & spaces'
        self.log = self.directory / 'commands.jsonl'
        shim = self.bin / 'shim'
        shim.write_text(f'''#!{sys.executable}
import json, os, pathlib, shutil, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ['SETUP_TEST_LOG'], 'a') as stream:
    stream.write(json.dumps([name, *args]) + '\\n')
if name == 'uname':
    print(os.environ['SETUP_TEST_OS'])
elif name == 'df':
    print('Filesystem 1024-blocks Used Available Capacity Mounted on')
    print('mock 99999999 0 ' + os.environ['SETUP_TEST_FREE'] + ' 0% /')
elif name == 'brew' and args[:1] == ['--prefix']:
    print(pathlib.Path(sys.argv[0]).parent.parent)
elif name == 'sudo':
    os.execvp(args[0], args)
elif name.startswith('python'):
    if args[:1] == ['-c'] or (args and args[0].endswith('setup.py') and 'plan' in args):
        os.execv({sys.executable!r}, [{sys.executable!r}, *args])
    elif args[:2] == ['-m', 'venv']:
        target = pathlib.Path(args[2]) / 'bin/python'
        target.parent.mkdir(parents=True)
        shutil.copy2(sys.argv[0], target)
''')
        shim.chmod(0o755)
        for name in ('python3', 'python3.12', 'uname', 'df', 'apt-get', 'apt-cache', 'sudo', 'brew'):
            (self.bin / name).symlink_to(shim)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
                        SETUP_TEST_LOG=str(self.log), SETUP_TEST_OS='Linux', SETUP_TEST_FREE='2')

    def launch(self, *args):
        return subprocess.run(['bash', str(ROOT / 'install.sh'), *args, '--home', str(self.home)],
                              env=self.env, capture_output=True, text=True, timeout=30)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_lightweight_linux_selections_skip_browser_prerequisites(self):
        for selection in ('context7', 'strix,skillui'):
            with self.subTest(selection=selection):
                result = self.launch('install', '--only', selection)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls()
        self.assertFalse(any(call[0] == 'df' for call in calls))
        packages = [call for call in calls if call[0] == 'apt-get']
        self.assertTrue(any('python3-venv' in call for call in packages))
        self.assertFalse(any('ffmpeg' in call or 'libnss3' in call for call in packages))
        self.assertFalse(any(call[0] in ('docker', 'strix') for call in calls))

    def test_lightweight_macos_selection_skips_ffmpeg(self):
        self.env['SETUP_TEST_OS'] = 'Darwin'
        result = self.launch('install', '--only=context7')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(['brew', 'install', 'git', 'python@3.12'], self.calls())
        self.assertFalse(any('ffmpeg' in call for call in self.calls()))

    def test_all_with_optional_components_retains_disk_preflight(self):
        result = self.launch('install', '--only', ' all ,strix,skillui')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('12 GiB', result.stderr)
        self.assertFalse(any(call[0] == 'apt-get' for call in self.calls()))
        self.assertFalse(self.home.exists())

    def test_all_with_optional_components_retains_browser_packages(self):
        self.env['SETUP_TEST_FREE'] = '99999999'
        result = self.launch('install', '--only', 'all,strix,skillui')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        packages = [call for call in self.calls() if call[0] == 'apt-get']
        self.assertTrue(any('ffmpeg' in call and 'libnss3' in call for call in packages))

    def test_invalid_selection_fails_before_system_changes(self):
        result = self.launch('install', '--only', 'context77')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unknown component', result.stderr)
        self.assertFalse(any(call[0] in ('apt-get', 'brew', 'df') for call in self.calls()))
        self.assertFalse(self.home.exists())

    def test_plan_expands_defaults_without_writes(self):
        result = self.launch('plan', '--only', 'all,strix,skillui')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        components = next(line for line in result.stdout.splitlines() if line.startswith('Components:'))
        self.assertTrue(all(name in components for name in ('hermes', 'context7', 'strix', 'skillui')))
        self.assertFalse(self.home.exists())
        self.assertFalse(any(call[0] in ('apt-get', 'brew', 'df') for call in self.calls()))


if __name__ == '__main__':
    unittest.main()
