"""Tests for the Codex MCP dotenv credential helper."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'mcp_headers.py'


class McpHeadersTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env_file = Path(self.tmp.name) / 'secrets.env'

    def run_helper(self):
        return subprocess.run([sys.executable, str(HELPER), '--env-file', str(self.env_file),
                               '--variable', 'LLM_GATEWAY_KEY'], capture_output=True, text=True)

    def test_reads_quoted_dotenv_value_without_logging_it(self):
        self.env_file.write_text('# private\nexport LLM_GATEWAY_KEY="token-value"\n')
        self.env_file.chmod(0o600)
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'Authorization': 'Bearer token-value'})

    @unittest.skipIf(os.name == 'nt', 'POSIX permission bits do not describe Windows ACLs')
    def test_rejects_group_readable_file_without_exposing_value(self):
        self.env_file.write_text('LLM_GATEWAY_KEY=do-not-print-this\n')
        self.env_file.chmod(0o644)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('do-not-print-this', result.stdout + result.stderr)

    def test_rejects_duplicates_and_header_injection(self):
        self.env_file.write_text('LLM_GATEWAY_KEY=first\nLLM_GATEWAY_KEY=second\n')
        self.env_file.chmod(0o600)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('first', result.stdout + result.stderr)
        self.assertNotIn('second', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
