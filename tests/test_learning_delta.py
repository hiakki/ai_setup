"""The delta checker must expose changes without treating observation as review."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'docs/tools/learning_delta.py'


class LearningDeltaTests(unittest.TestCase):
    def run_checker(self, root, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), *args],
                              capture_output=True, text=True)

    def test_detects_add_change_remove_without_exporting_contents(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'projects'
            root.mkdir()
            (root / 'old.md').write_text('private original text')
            (root / 'keep.md').write_text('original')
            baseline = Path(folder) / 'baseline.json'
            first = self.run_checker(root, '--snapshot', str(baseline))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertNotIn('private original text', baseline.read_text())
            self.assertEqual(json.loads(first.stdout)['added'], ['keep.md', 'old.md'])
            same = self.run_checker(root, '--baseline', str(baseline))
            self.assertEqual(same.returncode, 0, same.stderr)
            self.assertEqual(json.loads(same.stdout)['changed'], [])
            (root / 'old.md').unlink()
            (root / 'keep.md').write_text('changed')
            (root / 'new.md').write_text('new')
            result = self.run_checker(root, '--baseline', str(baseline))
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data['added'], ['new.md'])
            self.assertEqual(data['changed'], ['keep.md'])
            self.assertEqual(data['removed'], ['old.md'])
            self.assertFalse(data['semantic_review_performed'])

    def test_exclusions_symlinks_and_scope_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'projects'
            root.mkdir()
            for name in ['app/docs/a.md', 'private/p.md', 'app/node_modules/v.md', '.hidden/s.md']:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('text')
            try:
                (root / 'linked.md').symlink_to(root / 'private/p.md')
            except OSError:
                pass  # Windows may disallow symlinks; exclusion behavior still runs.
            baseline = Path(folder) / 'baseline.json'
            result = self.run_checker(root, '--exclude', 'private', '--snapshot', str(baseline))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['added'], ['app/docs/a.md'])
            mismatch = self.run_checker(root, '--baseline', str(baseline))
            self.assertEqual(mismatch.returncode, 2)
            self.assertIn('scope', mismatch.stderr.lower())

    def test_missing_root_invalid_baseline_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            invalid = root / 'invalid.json'
            invalid.write_text('{}')
            self.assertEqual(self.run_checker(root / 'missing').returncode, 2)
            self.assertEqual(self.run_checker(root, '--baseline', str(invalid)).returncode, 2)
            original = invalid.read_bytes()
            self.assertEqual(self.run_checker(root, '--snapshot', str(invalid)).returncode, 2)
            self.assertEqual(invalid.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
