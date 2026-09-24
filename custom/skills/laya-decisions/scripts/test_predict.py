"""Offline transport and credential regression tests; no real key or network."""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SCRIPT = Path(__file__).with_name('predict.py')
SPEC = importlib.util.spec_from_file_location('predict', SCRIPT)
client = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(client)
REQUEST = {'state': {'message': 'Please refund me.'}, 'questions': {
    'refund': {'type': 'noul', 'instructions': 'Is a refund requested?'}}}
RESPONSE = {'answers': {'refund': {'type': 'noul', 'noul': 0.95}}}
TOKEN = 'synthetic-test-token'


class PredictTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / 'config.json'
        self.config.write_text(json.dumps({'endpoint': 'https://example.invalid/predict', 'token': TOKEN}))
        if os.name == 'nt':
            self.set_windows_acl(public=False)
        else:
            self.config.chmod(0o600)

    def set_windows_acl(self, public):
        # Exercise the real filesystem DACL on Windows; fixture paths never enter PowerShell source.
        script = '''
$ErrorActionPreference = 'Stop'
$path = $env:LAYA_TEST_CONFIG
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$acl = Get-Acl -LiteralPath $path
$acl.SetOwner($sid)
$acl.SetAccessRuleProtection($true, $false)
foreach ($rule in @($acl.Access)) { $acl.RemoveAccessRuleSpecific($rule) }
$acl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($sid, 'FullControl', 'Allow'))
if ($env:LAYA_TEST_PUBLIC -eq '1') {
    $everyone = [System.Security.Principal.SecurityIdentifier]::new('S-1-1-0')
    $acl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($everyone, 'Read', 'Allow'))
}
# Persist only the changed access/owner sections. Set-Acl can request audit
# privileges when applying a replacement descriptor on Windows PowerShell 5.1.
([System.IO.FileInfo]::new($path)).SetAccessControl($acl)
'''
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                       env=dict(os.environ, LAYA_TEST_CONFIG=str(self.config),
                                LAYA_TEST_PUBLIC='1' if public else '0'), check=True,
                       capture_output=True)

    def run_cli(self, data=REQUEST, response=RESPONSE, failure=None):
        out, err = io.StringIO(), io.StringIO()
        raw = response if isinstance(response, bytes) else json.dumps(response).encode()
        with patch.dict(os.environ, {}, clear=True), \
             patch('sys.stdin', io.StringIO(json.dumps(data))), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
             patch.object(client.urllib.request.OpenerDirector, 'open') as transport:
            transport.return_value = io.BytesIO(raw)
            transport.side_effect = failure
            status = client.main(['--config', str(self.config)])
        return status, out.getvalue(), err.getvalue(), transport

    def test_posts_bearer_json_and_preserves_answers(self):
        status, out, err, transport = self.run_cli()
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(out), RESPONSE)
        req = transport.call_args.args[0]
        self.assertEqual(req.get_method(), 'POST')
        self.assertEqual(req.get_header('Authorization'), 'Bearer ' + TOKEN)
        self.assertEqual(json.loads(req.data), REQUEST)
        self.assertIn('elapsed_ms=', err)
        self.assertNotIn(TOKEN, out + err)

    def test_http_503_is_failure_without_html_or_secret_leak(self):
        error = HTTPError('https://example.invalid', 503, TOKEN, {}, io.BytesIO(TOKEN.encode()))
        status, out, err, _ = self.run_cli(failure=error)
        self.assertEqual(status, 1)
        self.assertEqual(out, '')
        self.assertIn('HTTP 503', err)
        self.assertNotIn(TOKEN, err)

    def test_timeout_is_failure_without_exception_detail_leak(self):
        for error in [TimeoutError(TOKEN), URLError(TOKEN)]:
            with self.subTest(error=type(error).__name__):
                status, out, err, _ = self.run_cli(failure=error)
                self.assertEqual(status, 1)
                self.assertEqual(out, '')
                self.assertNotIn(TOKEN, err)

    def test_rejects_invalid_request_before_network(self):
        for data in [{}, {'state': {}, 'questions': {}}, {'state': {}, 'questions': {'q': {'type': 'chat'}}}]:
            with self.subTest(data=data):
                status, _, _, transport = self.run_cli(data=data)
                self.assertEqual(status, 1)
                transport.assert_not_called()

    def test_rejects_non_json_and_missing_answers(self):
        for response in [b'<html>not a model response</html>', {}, {'answers': {}}]:
            with self.subTest(response=response):
                status, out, _, _ = self.run_cli(response=response)
                self.assertEqual(status, 1)
                self.assertEqual(out, '')

    def test_rejects_missing_key_insecure_url_and_public_config(self):
        for config in [{'endpoint': 'https://example.invalid/predict'},
                       {'endpoint': 'http://example.invalid/predict', 'token': TOKEN}]:
            self.config.write_text(json.dumps(config))
            status, _, _, transport = self.run_cli()
            self.assertEqual(status, 1)
            transport.assert_not_called()
        self.config.write_text(json.dumps({'endpoint': 'https://example.invalid/predict', 'token': TOKEN}))
        if os.name == 'nt':
            self.set_windows_acl(public=True)
        else:
            self.config.chmod(0o644)
        status, _, _, transport = self.run_cli()
        self.assertEqual(status, 1)
        transport.assert_not_called()

    def test_windows_acl_metadata_rejects_other_principals_and_unverifiable_acl(self):
        owner = 'S-1-5-21-123-456-789-1001'
        private = {'user': owner, 'owner': owner, 'allow': [owner, 'S-1-5-18', 'S-1-5-32-544']}
        with patch.object(client, 'windows_acl', return_value=private):
            client.require_private_config(self.config, windows=True)
        for metadata in [dict(private, allow=[owner, 'S-1-1-0']),
                         dict(private, owner='S-1-5-21-999-999-999-1001'),
                         {}, dict(private, allow=None)]:
            with self.subTest(metadata=metadata), patch.object(client, 'windows_acl', return_value=metadata):
                with self.assertRaises(ValueError):
                    client.require_private_config(self.config, windows=True)

    def test_redirect_handler_never_forwards_credentials(self):
        handler = client.NoRedirect()
        req = client.urllib.request.Request('https://example.invalid', headers={'Authorization': 'Bearer ' + TOKEN})
        self.assertIsNone(handler.redirect_request(req, None, 307, 'redirect', {}, 'https://elsewhere.invalid'))

    def test_environment_only_configuration_for_new_server(self):
        out = io.StringIO()
        with patch.dict(os.environ, {'LAYA_ENDPOINT': 'https://example.invalid/predict',
                                     'LAYA_API_TOKEN': TOKEN}, clear=True), \
             patch('sys.stdin', io.StringIO(json.dumps(REQUEST))), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()), \
             patch.object(client.urllib.request.OpenerDirector, 'open', return_value=io.BytesIO(json.dumps(RESPONSE).encode())):
            status = client.main(['--config', str(self.config.parent / 'missing.json')])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(out.getvalue()), RESPONSE)


if __name__ == '__main__':
    unittest.main()
