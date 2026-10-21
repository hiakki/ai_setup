import json
import http.server
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AgentWikiClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home with spaces'
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(handler):
                length = int(handler.headers.get('content-length', '0'))
                request = json.loads(handler.rfile.read(length))
                authenticated = handler.headers.get('authorization') == 'Bearer secret-must-not-persist'
                body = {'jsonrpc': '2.0', 'id': request.get('id')}
                if authenticated:
                    body['result'] = {'protocolVersion': '2025-03-26',
                                      'serverInfo': {'name': 'agent-wiki', 'version': 'test'}}
                    handler.send_response(200)
                else:
                    body['error'] = {'code': -32001, 'message': 'unauthorized'}
                    handler.send_response(401)
                encoded = json.dumps(body).encode()
                handler.send_header('Content-Type', 'application/json')
                handler.send_header('Content-Length', str(len(encoded)))
                handler.end_headers()
                handler.wfile.write(encoded)

            def log_message(handler, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.thread.join)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.endpoint = f'http://127.0.0.1:{self.server.server_port}/api/mcp'
        self.env = dict(os.environ, AGENT_WIKI_MCP_URL=self.endpoint,
                        AGENT_WIKI_TOKEN='secret-must-not-persist')

    def run_setup(self, action='install'):
        return subprocess.run([sys.executable, str(ROOT / 'setup.py'), action,
                               '--only', 'agentwiki', '--home', str(self.home)],
                              env=self.env, capture_output=True, text=True, timeout=30)

    def test_registers_both_clients_without_persisting_key(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        codex = tomllib.loads((self.home / '.codex/config.toml').read_text())
        entry = codex['mcp_servers']['agent-wiki']
        self.assertEqual(entry['url'], self.env['AGENT_WIKI_MCP_URL'])
        self.assertEqual(entry['bearer_token_env_var'], 'AGENT_WIKI_TOKEN')
        claude = json.loads((self.home / '.claude.json').read_text())
        self.assertEqual(claude['mcpServers']['agent-wiki']['headers'],
                         {'Authorization': 'Bearer ${AGENT_WIKI_TOKEN}'})
        guidance = (self.home / '.codex/AGENTS.md').read_text()
        self.assertIn('meaningful project checkpoint', guidance)
        self.assertIn('short hub plus focused domain pages', guidance)
        for path in self.home.rglob('*'):
            if path.is_file():
                self.assertNotIn(b'secret-must-not-persist', path.read_bytes(), str(path))
        self.env.pop('AGENT_WIKI_MCP_URL')
        for action in ('install', 'verify'):
            result = self.run_setup(action)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_non_https_remote_wrong_path_or_embedded_credentials(self):
        for endpoint in ('http://wiki.example.test/api/mcp', 'https://wiki.example.test/',
                         'https://user:secret@wiki.example.test/api/mcp',
                         'https://wiki.example.test/api/mcp?token=secret'):
            with self.subTest(endpoint=endpoint):
                self.env['AGENT_WIKI_MCP_URL'] = endpoint
                result = self.run_setup()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.home / '.codex/config.toml').exists())
                self.assertFalse((self.home / '.claude.json').exists())
                self.assertNotIn('user:secret', result.stdout + result.stderr)

    def test_rejects_invalid_api_key_during_remote_initialization(self):
        self.env['AGENT_WIKI_TOKEN'] = 'wrong-key-must-not-persist'
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('authenticated remote initialization verified', result.stdout)
        for path in self.home.rglob('*'):
            if path.is_file():
                self.assertNotIn(b'wrong-key-must-not-persist', path.read_bytes(), str(path))

    def test_preserves_existing_operator_entry(self):
        self.home.mkdir(parents=True)
        codex = self.home / '.codex/config.toml'
        codex.parent.mkdir()
        original = (f'[mcp_servers.agent-wiki]\nurl = "{self.endpoint}"\n'
                    'enabled = false\nbearer_token_env_var = "OPERATOR_TOKEN"\n')
        codex.write_text(original)
        claude = self.home / '.claude.json'
        body = {'mcpServers': {'agent-wiki': {'type': 'http',
                'url': self.endpoint,
                'headers': {'Authorization': 'Bearer operator-secret'}}}}
        claude.write_text(json.dumps(body))
        self.env.pop('AGENT_WIKI_MCP_URL')
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(codex.read_text(), original)
        self.assertEqual(json.loads(claude.read_text()), body)
        self.assertNotIn('operator-secret', (self.home / '.local/state/ai-setup/state.json').read_text())

    def test_default_profile_detects_api_key_alias_in_private_file(self):
        secret = self.home / '.config/ai-setup/secrets.env'
        secret.parent.mkdir(parents=True)
        secret.write_text('AGENT_WIKI_API_KEY=secret-must-not-persist\n')
        secret.chmod(0o600)
        env = dict(os.environ, AGENT_WIKI_MCP_URL=self.endpoint)
        result = subprocess.run([sys.executable, str(ROOT / 'setup.py'), 'plan', '--only', 'all',
                                 '--home', str(self.home)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('agentwiki', result.stdout.split('Components:', 1)[1].splitlines()[0])


if __name__ == '__main__':
    unittest.main()
