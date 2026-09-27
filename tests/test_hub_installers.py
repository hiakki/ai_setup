"""Selective shared updates, preserved provider revisions and launcher forwarding."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hub_setup', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SharedUpdateTests(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'POSIX shell launcher')
    def test_launcher_help_does_not_bootstrap_or_run_package_manager(self):
        binaries = self.directory / 'bin'
        binaries.mkdir()
        marker = self.directory / 'package-manager-called'
        for name, body in {
            'uname': '#!/bin/sh\nprintf Darwin',
            'brew': '#!/bin/sh\ntouch "$HELP_TEST_MARKER"\nexit 73',
        }.items():
            command = binaries / name
            command.write_text(body + '\n')
            command.chmod(0o755)
        environment = dict(os.environ, HOME=str(self.home),
                           PATH=str(binaries) + os.pathsep + os.environ['PATH'],
                           HELP_TEST_MARKER=str(marker))
        for args in (['--help'], ['-h'], ['install', '--help'], ['--only', 'custom', '--help']):
            with self.subTest(args=args):
                result = subprocess.run(['bash', str(ROOT / 'install.sh'), *args],
                                        env=environment, text=True, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('usage:', result.stdout)
                self.assertFalse(marker.exists())
                self.assertFalse(self.home.exists())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.home = self.directory / 'home with spaces'
        self.provider = self.directory / 'provider'
        skill = self.provider / 'example'
        skill.mkdir(parents=True)
        self.entry = skill / 'SKILL.md'
        self.entry.write_text('---\nname: example\ndescription: Test skill\n---\nFirst revision\n')
        self.git('init', '-q')
        self.commit('first')
        self.source = {'id': 'fixture', 'url': str(self.provider),
                       'revision': self.git('rev-parse', 'HEAD').strip(),
                       'skills': [{'name': 'example', 'path': 'example'}]}
        self.manifest = self.directory / 'manifest.json'
        self.save_manifest()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.provider), *args], text=True)

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', message)

    def save_manifest(self):
        self.manifest.write_text(json.dumps({'schema': 1, 'sources': [self.source]}))

    def run_setup(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'setup.py'), *args,
                               '--home', str(self.home), '--manifest', str(self.manifest)],
                              capture_output=True, text=True, timeout=60)

    def install_first(self):
        result = self.run_setup('install', '--only', 'skills')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def next_revision(self):
        self.entry.write_text(self.entry.read_text().replace('First revision', 'Second revision'))
        self.commit('second')
        self.source['revision'] = self.git('rev-parse', 'HEAD').strip()
        self.save_manifest()

    def test_update_changes_pin_without_resetting_previous_source_and_reinstall_reuses_it(self):
        self.install_first()
        original = self.home / '.agents/skills/.sources/fixture'
        (original / 'example/SKILL.md').write_text('Personal provider edits are retained.\n')
        (original / 'runtime-cache').write_text('Keep downloaded assets.\n')
        self.next_revision()
        rejected = self.run_setup('install', '--only', 'skills')
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('use update', rejected.stderr)
        result = self.run_setup('update')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('== runtime ==', result.stdout)
        self.assertNotIn('== custom ==', result.stdout)
        self.assertEqual((original / 'example/SKILL.md').read_text(), 'Personal provider edits are retained.\n')
        self.assertEqual((original / 'runtime-cache').read_text(), 'Keep downloaded assets.\n')
        newer = original.with_name('fixture-' + self.source['revision'])
        self.assertTrue(newer.is_dir())
        self.assertIn('Second revision', (self.home / '.agents/skills/example/SKILL.md').read_text())
        state = json.loads((self.home / '.local/state/ai-setup/state.json').read_text())
        self.assertEqual(state['completed'], ['skills'])
        self.assertEqual(state['sources']['fixture']['path'], newer.relative_to(self.home).as_posix())
        repeated = self.run_setup('install', '--only', 'skills')
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)

    def test_update_preserves_locally_edited_installed_skill(self):
        self.install_first()
        target = self.home / '.agents/skills/example/SKILL.md'
        target.write_text('Locally improved skill\n')
        self.next_revision()
        result = self.run_setup('update', '--only', 'skills')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('locally edited path', result.stderr)
        self.assertEqual(target.read_text(), 'Locally improved skill\n')

    def test_update_rejects_changed_origin(self):
        self.install_first()
        self.next_revision()
        self.source['url'] = 'https://example.invalid/unrelated.git'
        self.save_manifest()
        result = self.run_setup('update', '--only', 'skills')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('revision/origin changed', result.stderr)

    def test_update_rejects_runtime_before_writing(self):
        result = self.run_setup('update', '--only', 'runtime')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('shared content only', result.stderr)
        self.assertFalse(self.home.exists())

    def test_source_alias_cannot_escape_cache(self):
        installer = setup.Installer(self.home, {'sources': []}, allow_source_updates=True)
        for alias in ('../escaped', '/absolute', 'nested/name', 'Bad Alias'):
            with self.subTest(alias=alias), self.assertRaisesRegex(ValueError, 'Invalid source id'):
                installer.fetch(dict(self.source, id=alias))
        self.assertFalse(self.home.exists())


@unittest.skipIf(os.name == 'nt', 'Host launcher simulations require POSIX executable fixtures')
class UpdateLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.home = self.directory / 'home & spaces'
        self.log = self.directory / 'arguments.json'
        self.env = dict(os.environ, AI_SETUP_TEST_LOG=str(self.log), AI_SETUP_TEST_HOME=str(self.home))

    def python_fixture(self, platform):
        executable = self.home / '.local/share/ai-setup/venv' / platform
        executable.parent.mkdir(parents=True)
        executable.write_text(f'#!{sys.executable}\nimport json, os, pathlib, sys\n'
                              'pathlib.Path(os.environ["AI_SETUP_TEST_LOG"]).write_text(json.dumps(sys.argv[1:]))\n')
        executable.chmod(0o755)

    def test_bash_update_forwards_without_bootstrap(self):
        self.python_fixture('bin/python')
        result = subprocess.run(['bash', str(ROOT / 'install.sh'), 'update', '--home', str(self.home),
                                 '--only', 'custom,docs,hub'], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.log.read_text()), [str(ROOT / 'setup.py'), 'update',
                         '--home', str(self.home), '--only', 'custom,docs,hub'])

    def test_bash_update_missing_environment_is_actionable(self):
        result = subprocess.run(['bash', str(ROOT / 'install.sh'), 'update', '--home', str(self.home)],
                                env=self.env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Updates require an existing ai_setup', result.stderr)
        self.assertFalse(self.home.exists())

    def test_powershell_update_forwards_without_bootstrap(self):
        pwsh = shutil.which('pwsh') or ROOT / '.work/powershell/pwsh'
        if not Path(pwsh).is_file():
            self.skipTest('PowerShell is not available for the native launcher simulation')
        self.python_fixture('Scripts/python.exe')
        harness = self.directory / 'harness.ps1'
        harness.write_text('''$ErrorActionPreference = 'Stop'
. ./install.ps1
function Assert-NativeWindows { }
function Find-SetupPython { throw 'update must use the installed environment' }
function Enable-SetupGit { throw 'update must not bootstrap Git' }
function Install-SetupPython { throw 'update must not bootstrap Python' }
function Install-SetupBuildTools { throw 'update must not install build tools' }
Invoke-AISetup 'update' $env:AI_SETUP_TEST_HOME 'custom,docs,hub' (Get-Location).Path
''')
        result = subprocess.run([str(pwsh), '-NoLogo', '-NoProfile', '-File', str(harness)],
                                cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(self.log.read_text()), [str(ROOT / 'setup.py'), 'update',
                         '--home', str(self.home), '--only', 'custom,docs,hub'])
        shutil.rmtree(self.home)
        result = subprocess.run([str(pwsh), '-NoLogo', '-NoProfile', '-File', str(harness)],
                                cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Updates require an existing ai_setup', result.stderr)
        self.assertFalse(self.home.exists())


if __name__ == '__main__':
    unittest.main()
