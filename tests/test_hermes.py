import json
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT, main
from hermes_runtime import configure_skills, data_home, install, launcher, stage_command


class HermesTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home with spaces'
        self.installer = Installer(self.home, json.loads((ROOT / 'manifest.json').read_text()))

    def test_default_install_and_all_dispatch_hermes_without_opt_in(self):
        expected = ['runtime', 'skills', 'agents', 'custom', 'blog', 'gstack',
                    'integrations', 'context7', 'rules', 'figma', 'hermes']
        for arguments in ([], ['--only', 'all']):
            with self.subTest(arguments=arguments), ExitStack() as patches:
                calls = []
                patches.enter_context(patch.dict(os.environ, {'USERPROFILE': str(self.home)}))
                patches.enter_context(patch.object(Installer, 'verify'))
                patches.enter_context(patch('setup.run'))
                for name in expected:
                    action = lambda installer, name=name: calls.append(name)
                    if name in ('runtime', 'gstack', 'integrations', 'figma'):
                        module = 'windows_runtime' if os.name == 'nt' else 'runtime'
                        patches.enter_context(patch(module + '.' + name, new=action))
                    elif name == 'context7':
                        patches.enter_context(patch('context7_runtime.install', new=action))
                    else:
                        patches.enter_context(patch.object(Installer, name, new=action))
                patches.enter_context(patch.object(sys, 'argv', ['setup.py', 'install',
                    '--home', str(self.home), *arguments]))
                main()
                self.assertEqual(calls, expected)
                state = json.loads((self.home / '.local/state/ai-setup/state.json').read_text())
                self.assertIn('hermes', state['completed'])

    def test_merge_preserves_operator_settings_and_is_idempotent(self):
        path = data_home(self.installer) / 'config.yaml'
        path.parent.mkdir(parents=True)
        config = {'model': {'default': 'operator-model'}, 'skills': {
            'external_dirs': ['/another/collection'], 'create_dir': '/operator/learning'},
            'terminal': {'backend': 'docker'}}
        path.write_text(yaml.safe_dump(config), encoding='utf-8')
        configure_skills(self.installer)
        first = path.read_bytes()
        actual = yaml.safe_load(first)
        self.assertEqual(actual['model'], config['model'])
        self.assertEqual(actual['terminal'], config['terminal'])
        self.assertEqual(actual['skills']['create_dir'], '/operator/learning')
        self.assertEqual(actual['skills']['external_dirs'], [
            '/another/collection', str(self.home / '.agents/skills')])
        configure_skills(self.installer)
        self.assertEqual(path.read_bytes(), first)

    def test_malformed_config_is_preserved(self):
        path = data_home(self.installer) / 'config.yaml'
        path.parent.mkdir(parents=True)
        for content in ('- list\n', 'skills: false\n', 'skills:\n  external_dirs: string\n'):
            path.write_text(content, encoding='utf-8')
            with self.assertRaises(ValueError):
                configure_skills(self.installer)
            self.assertEqual(path.read_text(encoding='utf-8'), content)

    def test_native_windows_command_uses_powershell_and_separate_path_arguments(self):
        self.installer.windows = True
        self.installer.env['LOCALAPPDATA'] = str(self.home / 'AppData/Local')
        source = self.home / 'source with spaces'
        command = stage_command(self.installer, source, 'python-deps')
        self.assertEqual(command[0], 'powershell.exe')
        self.assertEqual(command[command.index('-InstallDir') + 1], source)
        self.assertIn('-SkipBrowser', command)
        self.assertNotIn('wsl', command)
        self.assertEqual(command[-2:], ['-Stage', 'python-deps'])
        exe = data_home(self.installer) / 'bin/hermes.exe'
        exe.parent.mkdir(parents=True)
        exe.touch()
        self.assertEqual(launcher(self.installer), exe)

    def test_alternate_windows_home_fails_before_fetch_or_registry_changes(self):
        self.installer.windows = True
        with patch.dict(os.environ, {'USERPROFILE': str(self.home.parent / 'real')}), \
                patch.object(self.installer, 'fetch') as fetch:
            with self.assertRaisesRegex(ValueError, 'current user'):
                install(self.installer)
            fetch.assert_not_called()

    @unittest.skipIf(os.name == 'nt', 'POSIX provider-stage fixture; native command contract tested separately')
    def test_real_cli_installs_retries_and_rejects_drift(self):
        source = self.home.parent / 'provider'
        (source / 'scripts').mkdir(parents=True)
        # Exercise the actual orchestration with a small provider, no model/network calls.
        (source / 'scripts/install.sh').write_text('''#!/bin/bash
set -eu
while [ "$#" -gt 0 ]; do
  case "$1" in
    --stage) stage="$2"; shift 2 ;;
    --dir|--hermes-home|--commit) shift 2 ;;
    *) shift ;;
  esac
done
mkdir -p "$HERMES_HOME" "$HOME/.local/bin"
echo "$stage" >> "$HERMES_HOME/stages"
if [ "$stage" = python-deps ] && [ -f "$HOME/fail-deps" ]; then exit 17; fi
if [ "$stage" = products ]; then
  printf '#!/bin/sh\\nprintf "Hermes fixture help\\\\n"\\n' > "$HOME/.local/bin/hermes"
  chmod +x "$HOME/.local/bin/hermes"
  if [ -f "$HOME/fail-products" ]; then exit 19; fi
fi
''', encoding='utf-8')
        def git(*args):
            return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Provider fixture')
        manifest = self.home.parent / 'manifest.json'
        manifest.write_text(json.dumps({'schema': 1, 'sources': [{
            'id': 'hermes-agent', 'url': str(source), 'revision': git('rev-parse', 'HEAD')}]}))
        def invoke(command='install', ok=True):
            result = subprocess.run([sys.executable, str(ROOT / 'setup.py'), command,
                                     '--only', 'hermes', '--home', str(self.home),
                                     '--manifest', str(manifest)], capture_output=True, text=True)
            self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
            return result
        self.home.mkdir()
        (self.home / 'fail-deps').touch()
        invoke(ok=False)
        state = self.home / '.local/state/ai-setup/state.json'
        self.assertNotIn('hermes', json.loads(state.read_text())['completed'])
        (self.home / 'fail-deps').unlink()
        (self.home / 'fail-products').touch()
        invoke(ok=False)
        self.assertNotIn('hermes', json.loads(state.read_text())['completed'])
        self.assertTrue((self.home / '.local/bin/hermes').exists())
        (self.home / 'fail-products').unlink()
        invoke()
        self.assertIn('hermes', json.loads(state.read_text())['completed'])
        self.assertTrue((self.home / '.claude/skills/hermes-workflows/SKILL.md').exists())
        for client in ('.codex/AGENTS.md', '.claude/CLAUDE.md'):
            self.assertIn('ai-setup:hermes:start', (self.home / client).read_text())
        invoke()  # Actual rerun and managed ownership, not just mock assertions.
        stages = (self.home / '.hermes/stages').read_text().splitlines()
        self.assertNotIn('repository', stages)
        self.assertNotIn('gateway', stages)
        self.assertNotIn('setup', stages)
        invoke('verify')
        provider = self.home / '.agents/skills/.sources/hermes-agent/scripts/install.sh'
        provider.write_text('local edit')
        invoke('verify', ok=False)
        invoke(ok=False)
        self.assertEqual(provider.read_text(), 'local edit')


if __name__ == '__main__':
    unittest.main()
