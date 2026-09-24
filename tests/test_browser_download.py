"""Exercise connection timeout handling with real Node requests and child processes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
PRELOAD = ROOT / 'config/playwright-download-timeout.cjs'


@unittest.skipUnless(NODE, 'Node is required for browser downloader regression tests')
class BrowserDownloadTests(unittest.TestCase):
    def test_timeout_covers_connection_setup_and_download_worker(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / '.work') as directory:
            script = Path(directory) / 'download worker.cjs'
            script.write_text('''
const assert = require('node:assert/strict');
const http = require('node:http');
const https = require('node:https');
const { fork } = require('node:child_process');
if (process.argv[2] === 'worker') {
  // Match the provider's forked downloader: execArgv carries --require.
  assert.equal(http.globalAgent.options.timeout, 2000);
  assert.equal(https.globalAgent.options.timeout, 2000);
  assert.equal(https.globalAgent.options.rejectUnauthorized, undefined);
  assert.equal(https.globalAgent.options.family, undefined);
  process.exit(0);
}

// Model Node's short agent timeout without relying on the external network.
http.globalAgent.options.timeout = 50;
if (process.env.SETUP_TEST_PRELOAD === '1')
  require(process.env.SETUP_TEST_PRELOAD_PATH);
const server = http.createServer((req, res) => res.end('downloaded'));
server.listen(0, '127.0.0.1', () => {
  const request = http.get({
    hostname: 'download.test', port: server.address().port,
    lookup(hostname, options, callback) {
      setTimeout(() => callback(null, options.all ?
        [{ address: '127.0.0.1', family: 4 }] : '127.0.0.1', 4), 300);
    }
  }, response => {
    let body = '';
    response.on('data', chunk => body += chunk);
    response.on('end', () => {
      assert.equal(body, 'downloaded');
      server.close();
      const child = fork(__filename, ['worker'], {
        execArgv: ['--require', process.env.SETUP_TEST_PRELOAD_PATH]
      });
      child.on('exit', code => { process.exitCode = code ?? 1; });
    });
  });
  // Like the pinned provider, setTimeout alone misses connection establishment.
  request.setTimeout(2000, () => request.destroy(new Error('connection timed out')));
  request.on('error', error => {
    console.error(error.message);
    process.exitCode = 1;
    server.close();
  });
});
''', encoding='utf-8')
            env = dict(os.environ, PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT='2000',
                       SETUP_TEST_PRELOAD_PATH=str(PRELOAD))
            for enabled in ('0', '1'):
                result = subprocess.run([NODE, str(script)],
                                        env=dict(env, SETUP_TEST_PRELOAD=enabled),
                                        capture_output=True, text=True, timeout=10)
                if enabled == '0':
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('connection timed out', result.stderr)
                else:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
