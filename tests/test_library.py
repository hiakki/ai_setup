"""Exercise central search and policy through real Git commits, not mocked hooks."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hub import Hub
import library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ai library ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / 'user home'
        self.home.mkdir()
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                        XDG_CONFIG_HOME=str(self.home / '.config'),
                        GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='Fixture',
                        GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_NAME='Fixture',
                        GIT_COMMITTER_EMAIL='fixture@example.invalid')
        for key in ('GIT_CONFIG_GLOBAL', 'GIT_CONFIG_COUNT', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
            self.env.pop(key, None)
        self.environment = patch.dict(os.environ, self.env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.hub = Hub(self.home)
        self.hub.root.mkdir(parents=True)
        for name in ('hub.py', 'library.py'):
            shutil.copy2(ROOT / name, self.hub.root / name)
        self.project = self.repo('consumer')
        self.central = self.repo('central')
        (self.central / 'custom/skills').mkdir(parents=True)
        (self.central / 'manifest.json').write_text('{}')
        (self.central / 'hub.py').write_text('# source marker')
        library.bind(self.hub, self.central)

    def git(self, root, *args, success=True):
        result = subprocess.run(['git', '-C', str(root), *args], text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def repo(self, name):
        root = self.root / name
        root.mkdir()
        self.git(root, 'init', '-q', '-b', 'main')
        self.git(root, 'commit', '--allow-empty', '-qm', 'Initial')
        return root

    def write(self, name, text='fixture', root=None):
        path = (root or self.project) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_search_canonical_provider_agents_and_docs_and_no_secret_or_link_reads(self):
        self.write('docs/shared/release.md', '# Release rollback', self.central)
        self.write('custom/skills/ci/SKILL.md', '# Release deployment', self.central)
        self.write('.agents/skills/provider/SKILL.md', '# Release provider', self.home)
        self.write('.codex/agents/reviewer.toml', 'description="Release review"', self.home)
        self.write('docs/.env', 'Release TOP_SECRET', self.central)
        outside = self.write('outside.md', 'Release EXTERNAL', self.root)
        try:
            (self.central / 'docs/external.md').symlink_to(outside)
        except OSError:
            pass  # Native Windows symlink privilege is not required for the other assertions.
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            hits = library.search(self.hub, 'release')
        self.assertEqual(len(hits), 4)
        self.assertIn('remote freshness not checked', out.getvalue())
        self.assertNotIn('TOP_SECRET', out.getvalue())
        self.assertNotIn('EXTERNAL', out.getvalue())

    def test_failed_refresh_never_returns_stale_search_as_fresh(self):
        with patch.object(self.hub, 'update', side_effect=ValueError('offline')):
            with self.assertRaisesRegex(ValueError, 'offline'):
                library.search(self.hub, 'release', refresh=True)

    def test_private_binding_is_explicit_and_missing_checkout_is_not_silent(self):
        private = self.repo('private-library')
        library.bind(self.hub, private, private=True)
        self.write('docs/projects/internal/context.md', 'Private internal context', private)
        self.assertEqual(len(library.search(self.hub, 'internal')), 1)
        private.rename(self.root / 'moved-library')
        with self.assertRaisesRegex(ValueError, 'missing'):
            library.search(self.hub, 'internal')

    def test_modified_dispatcher_and_operator_hook_config_are_preserved(self):
        library.install_guard(self.hub)
        hook = library.hooks_dir(self.hub) / 'pre-commit'
        original = hook.read_text()
        hook.write_text(original + '# Local change\n')
        with self.assertRaisesRegex(ValueError, 'Preserving'):
            library.install_guard(self.hub)
        self.assertIn('Local change', hook.read_text())
        with self.assertRaisesRegex(ValueError, 'edited'):
            library.guard_status(self.hub, self.project)
        self.git(self.project, 'config', '--global', 'core.hooksPath', 'operator-choice')
        with self.assertRaisesRegex(ValueError, 'independently'):
            library.remove_guard(self.hub)

    def test_real_commit_blocked_source_and_router_commit_allowed(self):
        library.install_guard(self.hub)
        self.write('docs/new guide.md')
        self.git(self.project, 'add', '.')
        rejected = self.git(self.project, 'commit', '-qm', 'Local docs', success=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('CENTRAL LIBRARY REQUIRED', rejected.stderr)
        self.git(self.project, 'reset', '-q')
        self.write('src/app.py', 'print(1)')
        self.write('AGENTS.md', 'Read the central library.')
        self.git(self.project, 'add', 'src/app.py', 'AGENTS.md')
        self.git(self.project, 'commit', '-qm', 'Code and routing')

    def test_central_checkout_allowed_but_same_named_project_is_not(self):
        library.install_guard(self.hub)
        self.write('custom/skills/new/SKILL.md', '# New', self.central)
        self.git(self.central, 'add', '.')
        self.git(self.central, 'commit', '-qm', 'Central authoring')
        impostor = self.repo('ai_setup')
        self.write('new/SKILL.md', '# Local', impostor)
        self.git(impostor, 'add', '.')
        self.assertNotEqual(self.git(impostor, 'commit', '-qm', 'Not central', success=False).returncode, 0)

    def test_existing_hooks_are_forwarded_and_can_reject(self):
        original = self.write('.git/hooks/pre-commit', '#!/bin/sh\nexit 17\n')
        original.chmod(0o755)
        library.install_guard(self.hub)
        self.write('app.py')
        self.git(self.project, 'add', '.')
        self.assertNotEqual(self.git(self.project, 'commit', '-qm', 'Original rejects', success=False).returncode, 0)
        original.write_text('#!/bin/sh\nprintf preserved > hook-result\n', encoding='utf-8')
        self.git(self.project, 'commit', '-qm', 'Original succeeds')
        self.assertEqual((self.project / 'hook-result').read_text(), 'preserved')

    def test_hook_stdin_arguments_and_exit_code_are_preserved(self):
        hook = self.write('.git/hooks/pre-push', '#!/bin/sh\nprintf "%s\\n" "$@" > hook-args\ncat > hook-input\nexit 23\n')
        hook.chmod(0o755)
        library.install_guard(self.hub)
        result = subprocess.run([sys.executable, str(self.hub.root / 'hub.py'), '--home', str(self.home),
                                 'git-hook', 'pre-push', 'origin', 'path with spaces'],
                                cwd=self.project, input='refs/heads/main abc refs/heads/main def\n',
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
        self.assertEqual((self.project / 'hook-args').read_text(), 'origin\npath with spaces\n')
        self.assertEqual((self.project / 'hook-input').read_text(), 'refs/heads/main abc refs/heads/main def\n')
        hook.write_text(hook.read_text().removeprefix('#!/bin/sh\n'))
        result = subprocess.run([sys.executable, str(self.hub.root / 'hub.py'), '--home', str(self.home),
                                 'git-hook', 'pre-push', 'origin', 'path with spaces'],
                                cwd=self.project, input='second payload\n', text=True, capture_output=True)
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
        self.assertEqual((self.project / 'hook-input').read_text(), 'second payload\n')

    def test_previous_global_hooks_and_post_commit_preserved_after_repeat_and_remove(self):
        previous = self.root / 'old hooks'
        previous.mkdir()
        hook = previous / 'post-commit'
        hook.write_text('#!/bin/sh\nprintf forwarded > post-result\n', encoding='utf-8')
        hook.chmod(0o755)
        self.git(self.project, 'config', '--global', 'core.hooksPath', previous.as_posix())
        library.install_guard(self.hub)
        library.install_guard(self.hub)
        self.write('app.py')
        self.git(self.project, 'add', '.')
        self.git(self.project, 'commit', '-qm', 'Forward post hook')
        self.assertEqual((self.project / 'post-result').read_text(), 'forwarded')
        library.remove_guard(self.hub)
        self.assertEqual(self.git(self.project, 'config', '--global', '--get', 'core.hooksPath').stdout.strip(), previous.as_posix())

    def test_check_reads_index_not_worktree_and_ci_range_catches_bypass(self):
        base = self.git(self.project, 'rev-parse', 'HEAD').stdout.strip()
        path = self.write('.claude/agents/new.md')
        self.git(self.project, 'add', '-f', str(path))
        path.unlink()
        with self.assertRaises(ValueError):
            library.check(self.hub, self.project)
        self.git(self.project, '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Bypassed locally')
        with self.assertRaises(ValueError):
            library.check(self.hub, self.project, base=base)

    def test_ignored_skill_is_visible_to_audit_and_hook_override_reported(self):
        self.write('.gitignore', '.agents/\n')
        self.write('.agents/skills/ci/SKILL.md')
        with self.assertRaises(ValueError):
            library.check(self.hub, self.project, audit=True)
        library.install_guard(self.hub)
        library.guard_status(self.hub, self.project)
        self.git(self.project, 'config', 'core.hooksPath', 'different-hooks')
        with self.assertRaisesRegex(ValueError, 'does not use'):
            library.guard_status(self.hub, self.project)

    def test_existing_docs_untouched_deletions_allowed_and_filename_patterns(self):
        self.write('docs/existing.md')
        self.git(self.project, 'add', '.')
        self.git(self.project, 'commit', '-qm', 'Existing docs')
        library.install_guard(self.hub)
        self.write('app.py')
        self.git(self.project, 'add', 'app.py')
        self.git(self.project, 'commit', '-qm', 'Unrelated code')
        self.git(self.project, 'rm', 'docs/existing.md')
        self.git(self.project, 'commit', '-qm', 'Retire local doc')
        for path in ('notes/new.md', '.agents/skills/test/helper.py', '.codex/agents/new.toml', 'Docs/spec.json', 'nested/SKILL.md'):
            self.assertIsNotNone(library.reason(path), path)
        self.assertIsNone(library.reason('src/agents/handler.py'))


if __name__ == '__main__':
    unittest.main()
