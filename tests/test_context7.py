import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import DEFAULT_COMPONENTS, Installer, ROOT, select_components
from context7_runtime import URL, install, verify


class Context7Tests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home with spaces'
        self.i = Installer(self.home, {'schema': 1, 'sources': []})

    def test_install_rerun_and_missing_registration(self):
        install(self.i)
        codex = self.home / '.codex/config.toml'
        claude = self.home / '.claude.json'
        self.assertEqual(tomllib.loads(codex.read_text())['mcp_servers']['context7']['url'], URL)
        self.assertEqual(json.loads(claude.read_text())['mcpServers']['context7']['type'], 'http')
        first = [p.read_bytes() for p in (codex, claude, self.home / '.codex/AGENTS.md')]
        install(self.i)
        self.assertEqual(first, [p.read_bytes() for p in (codex, claude, self.home / '.codex/AGENTS.md')])
        self.i.verify()
        claude.write_text('{}')
        with self.assertRaises(ValueError):
            verify(self.i)

    def test_existing_auth_stdio_and_disable_settings_preserved_without_secret_copy(self):
        codex = self.home / '.codex/config.toml'
        codex.parent.mkdir(parents=True)
        original = '[mcp_servers.context7]\ncommand = "custom-command"\nenabled = false\nargs = ["operator-secret"]\n'
        codex.write_text(original)
        claude = self.home / '.claude.json'
        body = {'mcpServers': {'context7': {'type': 'http', 'url': URL + '/oauth',
                 'headers': {'Authorization': 'Bearer operator-secret'}}}}
        claude.write_text(json.dumps(body))
        install(self.i)
        self.assertEqual(codex.read_text(), original)
        self.assertEqual(json.loads(claude.read_text()), body)
        self.assertNotIn('operator-secret', self.i.state_file.read_text())
        self.assertNotIn('operator-secret', json.dumps(self.i.state))

    def test_invalid_existing_entry_fails_before_other_client_is_written(self):
        self.home.mkdir(parents=True)
        (self.home / '.claude.json').write_text('{"mcpServers":{"context7":{}}}')
        with self.assertRaises(ValueError):
            install(self.i)
        self.assertFalse((self.home / '.codex/config.toml').exists())

    def test_operator_can_change_transport_after_initial_install(self):
        install(self.i)
        path = self.home / '.codex/config.toml'
        edited = '[mcp_servers.context7]\ncommand = "my-context7-wrapper"\n'
        path.write_text(edited)
        self.i.state['completed'] = ['context7']
        self.i.save()
        self.i.verify()
        install(self.i)
        self.i.verify()
        self.assertEqual(path.read_text(), edited)

    def test_actual_selective_command_and_verify(self):
        for command in ('install', 'install', 'verify'):
            result = subprocess.run([sys.executable, str(ROOT / 'setup.py'), command,
                                     '--only', 'context7', '--home', str(self.home)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads(self.i.state_file.read_text())
        self.assertEqual(state['completed'], ['context7'])
        self.assertEqual(state['sources'], {})

    def test_optional_selection_is_explicit_and_defaults_still_work(self):
        self.assertEqual(select_components('all'), list(DEFAULT_COMPONENTS))
        self.assertEqual(select_components(' all, strix,skillui,strix '),
                         list(DEFAULT_COMPONENTS) + ['strix', 'skillui'])
        self.assertEqual(select_components('context7'), ['context7'])
        for value in ('', 'all,', 'wrong'):
            with self.assertRaises(ValueError):
                select_components(value)


if __name__ == '__main__':
    unittest.main()
