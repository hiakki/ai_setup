"""Exercise optional remote-memory setup without network or credential persistence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HindsightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home with spaces'
        self.env = dict(os.environ)
        for key in ('HINDSIGHT_MCP_URL', 'HINDSIGHT_MCP_TOKEN_ENV'):
            self.env.pop(key, None)
        self.env.update(HINDSIGHT_MCP_URL='https://memory.example.test/mcp/shared/',
                        LLM_GATEWAY_KEY='test-secret-must-not-persist')

    def run_setup(self, action='install'):
        return subprocess.run([sys.executable, str(ROOT / 'setup.py'), action,
                               '--only', 'hindsight', '--home', str(self.home)],
                              env=self.env, capture_output=True, text=True, timeout=30)

    def test_registers_both_clients_with_environment_references_and_reruns_without_url(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        codex = self.home / '.codex/config.toml'
        claude = self.home / '.claude.json'
        self.assertEqual(tomllib.loads(codex.read_text())['mcp_servers']['hindsight'], {
            'url': 'https://memory.example.test/mcp/shared/',
            'bearer_token_env_var': 'LLM_GATEWAY_KEY'})
        self.assertEqual(json.loads(claude.read_text())['mcpServers']['hindsight'], {
            'type': 'http', 'url': 'https://memory.example.test/mcp/shared/',
            'headers': {'Authorization': 'Bearer ${LLM_GATEWAY_KEY}'}})
        first = [p.read_bytes() for p in (codex, claude)]
        self.env.pop('HINDSIGHT_MCP_URL')
        for action in ('install', 'update', 'verify'):
            result = self.run_setup(action)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(first, [p.read_bytes() for p in (codex, claude)])
        for p in self.home.rglob('*'):
            if p.is_file():
                self.assertNotIn(b'test-secret-must-not-persist', p.read_bytes(), str(p))

    def test_missing_or_unsafe_endpoint_and_invalid_variable_fail_before_registration(self):
        for value in ('', 'http://remote.example/mcp/shared/', 'https://user:password@memory.example/mcp/',
                      'https://memory.example/mcp/?key=secret', 'https://memory.example/mcp/#fragment'):
            with self.subTest(value=value):
                self.env['HINDSIGHT_MCP_URL'] = value
                result = self.run_setup()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.home / '.claude.json').exists())
                self.assertFalse((self.home / '.codex/config.toml').exists())
                self.assertNotIn('password', result.stdout + result.stderr)
        self.env['HINDSIGHT_MCP_URL'] = 'https://memory.example/mcp/shared/'
        self.env['HINDSIGHT_MCP_TOKEN_ENV'] = 'BAD-NAME'
        self.assertNotEqual(self.run_setup().returncode, 0)
        self.assertFalse((self.home / '.claude.json').exists())

    def test_custom_token_variable_and_loopback_http_work_without_a_key_at_install(self):
        self.env.update(HINDSIGHT_MCP_URL='http://127.0.0.1:8888/mcp/shared/',
                        HINDSIGHT_MCP_TOKEN_ENV='MEMORY_TOKEN')
        self.env.pop('LLM_GATEWAY_KEY')
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        cfg = tomllib.loads((self.home / '.codex/config.toml').read_text())
        self.assertEqual(cfg['mcp_servers']['hindsight']['bearer_token_env_var'], 'MEMORY_TOKEN')
        self.assertIn('MEMORY_TOKEN', result.stdout)

    def test_preserves_existing_auth_and_disabled_settings_without_recording_credentials(self):
        self.home.mkdir(parents=True)
        path = self.home / '.claude.json'
        body = {'mcpServers': {'hindsight': {'type': 'http',
            'url': self.env['HINDSIGHT_MCP_URL'], 'headers': {'Authorization': 'Bearer operator-secret'}},
            'other': {'command': 'preserve-me'}}, 'operatorSetting': True}
        path.write_text(json.dumps(body))
        codex = self.home / '.codex/config.toml'
        codex.parent.mkdir()
        original = '[mcp_servers.hindsight]\nurl = "https://memory.example.test/mcp/shared/"\nenabled = false\nbearer_token_env_var = "OPERATOR_TOKEN"\n'
        codex.write_text(original)
        self.env.pop('HINDSIGHT_MCP_URL')
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(path.read_text()), body)
        self.assertEqual(codex.read_text(), original)
        state = (self.home / '.local/state/ai-setup/state.json').read_text()
        self.assertNotIn('operator-secret', state)

    def test_invalid_or_conflicting_existing_config_does_not_partially_register(self):
        self.home.mkdir(parents=True)
        path = self.home / '.claude.json'
        for entry in (None, {}, {'type': 'http', 'url': 'https://different.example/mcp/private/'}):
            body = {'mcpServers': {'hindsight': entry}}
            path.write_text(json.dumps(body))
            result = self.run_setup()
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(path.read_text()), body)
            self.assertFalse((self.home / '.codex/config.toml').exists())

    def test_verify_detects_removed_registration(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (self.home / '.claude.json').write_text('{}')
        self.assertNotEqual(self.run_setup('verify').returncode, 0)


if __name__ == '__main__':
    unittest.main()
