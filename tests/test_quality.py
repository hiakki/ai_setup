import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT, select_components
import quality_runtime as quality

spec = importlib.util.spec_from_file_location('agent_provider', ROOT / 'evaluations/quality/agent_provider.py')
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)


class QualityTests(unittest.TestCase):
    def test_default_profile_and_supported_platforms(self):
        self.assertIn('quality', select_components('all'))
        with tempfile.TemporaryDirectory() as tmp:
            i = Installer(Path(tmp), {})
            for system, machine, expected in [('Darwin','arm64',('Darwin','arm64')),
                                               ('Linux','x86_64',('Linux','x64')),
                                               ('Linux','aarch64',('Linux','arm64'))]:
                i.windows = False
                with patch('platform.system', return_value=system), patch('platform.machine', return_value=machine):
                    self.assertEqual(quality.target(i), expected)
            i.windows = True
            with patch('platform.machine', return_value='AMD64'):
                self.assertEqual(quality.target(i), ('Windows','x64'))
            with patch('platform.machine', return_value='ARM64'):
                with self.assertRaises(ValueError): quality.target(i)

    def test_launchers_preserve_user_files_and_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            i = Installer(Path(tmp) / 'home with spaces', {})
            quality.write_launcher(i, 'example', [sys.executable, '-c', 'import sys; sys.exit(7)'])
            command = i.bin / ('example.cmd' if i.windows else 'example')
            self.assertEqual(subprocess.run([str(command)], shell=i.windows).returncode, 7)
            command.write_text('user changes')
            with self.assertRaisesRegex(ValueError, 'Preserving'):
                quality.write_launcher(i, 'example', [sys.executable])

    def test_windows_launcher_quotes_and_preserves_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            i = Installer(Path(tmp), {}); i.windows = True
            quality.write_launcher(i, 'tool', [Path(tmp) / 'with spaces/node.exe', 'script.js'])
            text = (i.bin / 'tool.cmd').read_text()
            self.assertIn('DisableDelayedExpansion', text)
            self.assertIn('exit /b %errorlevel%', text)
            self.assertIn('PROMPTFOO_DISABLE_TELEMETRY=1', text)

    def test_evaluation_is_opt_in(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn('error', provider.call_api('bug', {}, {'vars': {'task': 'bug'}}))

    def test_oracle_rejects_claimed_success_and_checks_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'app.py').write_text('def total(values):\n    return 42 # all tests passed\n')
            self.assertFalse(provider.grade('bug', root)[0])
            (root / 'app.py').write_text('def total(values):\n    return sum(values)\n')
            self.assertTrue(provider.grade('bug', root)[0])
            (root / 'answer.json').write_text('{"source":"history.md","retry_auth_failures":true}')
            self.assertFalse(provider.grade('recall', root)[0])
            (root / 'answer.json').write_text(json.dumps({'source':'current.md','revision':'fixture-v1',
                'retry_auth_failures':False,'bounded_backoff':True}))
            self.assertTrue(provider.grade('recall', root)[0])

    def test_instruction_deduplication_is_exact_and_idempotent(self):
        from quality_runtime import deduplicate_workflow
        with tempfile.TemporaryDirectory() as tmp:
            i = Installer(Path(tmp), {})
            p = i.home / '.codex/AGENTS.md'; p.parent.mkdir()
            body = (ROOT / 'config/WORKFLOW_RULES.md').read_text().strip()
            p.write_text('Keep personal rule.\n\n' + body + '\n')
            i.merge_text(p, body, 'workflow')
            deduplicate_workflow(i)
            self.assertEqual(p.read_text().count(body), 1)
            self.assertIn('Keep personal rule.', p.read_text())
            first = p.read_bytes(); deduplicate_workflow(i)
            self.assertEqual(p.read_bytes(), first)
            # Similar user wording must never be removed.
            p.write_text('PERSONAL ' + body.replace('Finish', 'Complete', 1) + '\n' + p.read_text())
            deduplicate_workflow(i)
            self.assertIn('PERSONAL', p.read_text())

    def test_remaining_oracles_have_positive_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'app.py').write_text(provider.CASES['refactor'][0]['app.py'])
            self.assertFalse(provider.grade('refactor', root)[0])
            (root / 'app.py').write_text('def classify(n):\n    return "negative" if n < 0 else "zero" if n == 0 else "positive"\n')
            self.assertTrue(provider.grade('refactor', root)[0])
            (root / 'index.html').write_text('<main><input type="email"><button>Save</button></main>')
            self.assertFalse(provider.grade('responsive', root)[0])
            (root / 'index.html').write_text('<meta name="viewport" content="width=device-width"><style>@media(max-width:600px){main{width:100%}}</style><main><label for="email">Email</label><input id="email" type="email"><button>Save</button></main>')
            self.assertTrue(provider.grade('responsive', root)[0])
            (root / 'answer.json').write_text('{"total":16,"source":"invented.json"}')
            self.assertFalse(provider.grade('recovery', root)[0])
            (root / 'answer.json').write_text('{"total":16,"source":"data/input.json"}')
            self.assertTrue(provider.grade('recovery', root)[0])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'answer.txt').write_text('4')
            self.assertTrue(provider.grade('irrelevant', root)[0])
            (root / 'unnecessary.md').write_text('Unrequested output')
            self.assertFalse(provider.grade('irrelevant', root)[0])


if __name__ == '__main__':
    unittest.main()
