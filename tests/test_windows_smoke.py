import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from smoke import RPC, main


class SmokeTransportTests(unittest.TestCase):
    def test_failed_rerun_replaces_previous_pass_report(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'state'
            state.mkdir()
            report = state / 'smoke-report.json'
            report.write_text(json.dumps({'status': 'passed'}))
            installer = SimpleNamespace(state_dir=state)
            with patch('smoke.Installer', return_value=installer), \
                    patch('smoke.check_runtime', side_effect=RuntimeError('Browser exited before click')), \
                    patch.object(sys, 'argv', ['smoke.py', '--home', directory]):
                with self.assertRaisesRegex(RuntimeError, 'Browser exited before click'):
                    main()
            evidence = json.loads(report.read_text())
            self.assertEqual(evidence['status'], 'failed')
            self.assertEqual(evidence['error'], 'Browser exited before click')

    def test_failed_initialize_closes_child_and_log(self):
        with tempfile.TemporaryDirectory() as directory:
            processes = []
            real_popen = subprocess.Popen

            def launch(*args, **kwargs):
                child = real_popen(*args, **kwargs)
                processes.append(child)
                return child

            program = ('import json,sys\n'
                       'for line in sys.stdin:\n'
                       ' request=json.loads(line)\n'
                       ' print(json.dumps({"id":request["id"],"error":{"message":"fixture rejected initialize"}}),flush=True)\n')
            try:
                with patch('smoke.subprocess.Popen', side_effect=launch):
                    with self.assertRaisesRegex(RuntimeError, 'fixture rejected initialize'):
                        RPC([sys.executable, '-u', '-c', program], dict(os.environ), Path(directory))
                self.assertIsNotNone(processes[0].poll(), 'Failed initialization leaked a child process')
                self.assertTrue(processes[0].stdin.closed)
                self.assertTrue(processes[0].stdout.closed)
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=10)

    def test_rpc_preserves_unicode_over_real_process_transport(self):
        program = ('import json,sys\n'
                   'for line in sys.stdin:\n'
                   ' request=json.loads(line)\n'
                   ' if "id" in request:\n'
                   '  print(json.dumps({"id":request["id"],"result":{"text":"Verified \\u2713"}},ensure_ascii=False),flush=True)\n')
        with tempfile.TemporaryDirectory(prefix='smoke home ') as directory:
            env = dict(os.environ, PYTHONIOENCODING='utf-8')
            with contextlib.closing(RPC([sys.executable, '-u', '-c', program], env, Path(directory))) as rpc:
                self.assertEqual(rpc.call('fixture/echo', {})['text'], 'Verified ✓')


if __name__ == '__main__':
    unittest.main()
