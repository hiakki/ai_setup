"""Check real HTTP MCP negotiation without reading or writing memories."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HindsightConnectionTests(unittest.TestCase):
    def test_handshake_pagination_and_auth_failure_are_reported_without_secret_output(self):
        calls = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                if self.headers.get('Authorization') != 'Bearer fixture-secret':
                    self.send_response(401)
                    self.end_headers()
                    return
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                calls.append((body, self.headers.get('Mcp-Session-Id')))
                method = body['method']
                if method == 'notifications/initialized':
                    self.send_response(202)
                    self.end_headers()
                    return
                if method == 'initialize':
                    result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                              'serverInfo': {'name': 'fixture', 'version': '1'}}
                elif method == 'tools/list':
                    result = ({'tools': [{'name': 'reflect'}]} if body.get('params', {}).get('cursor')
                              else {'tools': [{'name': 'retain'}, {'name': 'recall'}], 'nextCursor': 'page2'})
                else:
                    self.send_response(400)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header('Mcp-Session-Id', 'fixture-session')
                self.send_header('Content-Type', 'text/event-stream')
                self.end_headers()
                self.wfile.write(('event: message\ndata: ' + json.dumps(
                    {'jsonrpc': '2.0', 'id': body['id'], 'result': result}) + '\n\n').encode())

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            (home / '.codex').mkdir()
            url = f'http://127.0.0.1:{server.server_port}/mcp/shared/'
            (home / '.codex/config.toml').write_text(
                f'[mcp_servers.hindsight]\nurl = "{url}"\nbearer_token_env_var = "TEST_MEMORY_KEY"\n')
            (home / '.claude.json').write_text(json.dumps({'mcpServers': {'hindsight': {
                'type': 'http', 'url': url, 'headers': {'Authorization': 'Bearer ${TEST_MEMORY_KEY}'}}}}))
            command = [sys.executable, str(ROOT / 'tests/check_hindsight.py'), '--home', str(home)]
            env = dict(os.environ, TEST_MEMORY_KEY='fixture-secret')
            success = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(success.returncode, 0, success.stdout + success.stderr)
            self.assertIn('3 tools', success.stdout)
            self.assertNotIn('fixture-secret', success.stdout + success.stderr)
            self.assertEqual([c[0]['method'] for c in calls],
                             ['initialize', 'notifications/initialized', 'tools/list', 'tools/list'])
            self.assertTrue(all(c[1] == 'fixture-session' for c in calls[1:]))
            failed = subprocess.run(command, env=dict(env, TEST_MEMORY_KEY='wrong'),
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('HTTP 401', failed.stderr)
            self.assertEqual(len(calls), 4)


if __name__ == '__main__':
    unittest.main()
