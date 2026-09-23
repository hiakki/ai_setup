import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        work = REPO / '.work'
        work.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=work)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home with spaces'
        self.source = self.root / 'provider'
        skill = self.source / 'skills/example'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: example\ndescription: Example skill\n---\nRead references/details.md and ../../shared.md\n')
        (self.source / 'shared.md').write_text('Provider-level reference\n')
        (skill / 'references').mkdir()
        (skill / 'references/details.md').write_text('Supporting asset\n')
        (skill / 'scripts').mkdir()
        (skill / 'scripts/helper.py').write_text('def answer():\n    return 42\n')
        agent = self.source / 'agents'
        agent.mkdir()
        (agent / 'reviewer.md').write_text('---\nname: Test Reviewer\ndescription: Reviews code\n---\nCheck real behavior.\n')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Fixture')
        self.revision = self.git('rev-parse', 'HEAD').strip()
        self.manifest = self.root / 'manifest.json'
        self.data = {'schema': 1, 'sources': [{'id': 'example', 'url': str(self.source),
                     'revision': self.revision, 'skills': [{'path': 'skills/example', 'name': 'example',
                     'extra_files': {'shared.md': 'references/shared.md'},
                     'link_rewrites': {'../../shared.md': 'references/shared.md'}}],
                     'agents': ['agents/reviewer.md']}], 'npm': {}}
        self.manifest.write_text(json.dumps(self.data))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], text=True)

    def run_setup(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(REPO / 'setup.py'), *args,
                                 '--home', str(self.home), '--manifest', str(self.manifest)],
                                text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_plan_does_not_create_home_or_fetch(self):
        self.run_setup('plan')
        self.assertFalse(self.home.exists())

    def test_real_install_assets_roles_rules_and_idempotence(self):
        self.home.mkdir()
        config = self.home / '.codex/AGENTS.md'
        config.parent.mkdir()
        config.write_text('Existing personal rule.\n')
        self.run_setup('install', '--only', 'skills,agents,rules')
        skill = self.home / '.agents/skills/example'
        self.assertEqual((skill / 'references/details.md').read_text(), 'Supporting asset\n')
        self.assertEqual((skill / 'references/shared.md').read_text(), 'Provider-level reference\n')
        self.assertIn('references/shared.md', (skill / 'SKILL.md').read_text())
        self.assertEqual((self.home / '.claude/skills/example').resolve(), skill.resolve())
        self.assertTrue((self.home / '.codex/agents/test-reviewer.toml').is_file())
        self.assertIn('Existing personal rule.', config.read_text())
        before = config.read_bytes()
        self.run_setup('install', '--only', 'skills,agents,rules')
        self.assertEqual(config.read_bytes(), before)
        env = dict(__import__('os').environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'))
        ignored = subprocess.run(['git', '-C', str(self.source), 'check-ignore', '--no-index', '.agents/project-context.md'],
                                 env=env, text=True, capture_output=True)
        self.assertEqual(ignored.returncode, 0, ignored.stderr)
        self.run_setup('verify')

    def test_modified_global_rules_are_preserved(self):
        self.run_setup('install', '--only', 'rules')
        path = self.home / '.codex/AGENTS.md'
        content = path.read_text().replace('ai-setup:rules:start -->', 'ai-setup:rules:start -->\nMy change')
        path.write_text(content)
        self.run_setup('install', '--only', 'rules', ok=False)
        self.assertEqual(path.read_text(), content)

    def test_python_helper_execution_does_not_look_like_a_user_edit(self):
        self.run_setup('install', '--only', 'skills')
        scripts = self.home / '.agents/skills/example/scripts'
        subprocess.run([sys.executable, '-c',
                        'import sys; sys.path.insert(0, sys.argv[1]); import helper; assert helper.answer() == 42',
                        str(scripts)], check=True)
        self.assertTrue((scripts / '__pycache__').is_dir())
        self.run_setup('verify')
        self.run_setup('install', '--only', 'skills')

    def test_unmanaged_skill_collision_is_preserved(self):
        target = self.home / '.agents/skills/example'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('My skill')
        self.run_setup('install', '--only', 'skills', ok=False)
        self.assertEqual((target / 'SKILL.md').read_text(), 'My skill')

    def test_local_asset_edit_blocks_rerun_and_verify(self):
        self.run_setup('install', '--only', 'skills')
        target = self.home / '.agents/skills/example/references/details.md'
        target.write_text('My edit')
        self.run_setup('install', '--only', 'skills', ok=False)
        self.run_setup('verify', ok=False)
        self.assertEqual(target.read_text(), 'My edit')

    def test_wrong_revision_fails_without_installed_skill(self):
        self.data['sources'][0]['revision'] = '0' * 40
        self.manifest.write_text(json.dumps(self.data))
        self.run_setup('install', '--only', 'skills', ok=False)
        self.assertFalse((self.home / '.agents/skills/example').exists())

    def test_parent_directory_link_cannot_escape_home(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.home.mkdir()
        target = self.home / '.agents'
        if os.name == 'nt':
            import _winapi
            _winapi.CreateJunction(str(outside), str(target))
        else:
            target.symlink_to(outside, target_is_directory=True)
        self.run_setup('install', '--only', 'skills', ok=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_unknown_component_fails_before_writing(self):
        self.run_setup('install', '--only', 'skils', ok=False)
        self.assertFalse(self.home.exists())


if __name__ == '__main__':
    unittest.main()
