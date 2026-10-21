import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from setup import Installer, ROOT, select_components
from agentreach_runtime import install_skill, paths, write_launcher, install


class AgentReachTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home with spaces'
        self.manifest = json.loads((ROOT / 'manifest.json').read_text())
        self.i = Installer(self.home, self.manifest)

    def test_default_and_standalone_selection(self):
        self.assertIn('agentreach', select_components('all'))
        self.assertEqual(select_components('agentreach'), ['agentreach'])
        with self.assertRaises(ValueError):
            select_components('agent-reach')

    def test_dependency_only_update_gets_separate_runtime(self):
        original = paths(self.i)[0]
        self.manifest['agent_reach']['yt_dlp'] = '2099.1.1'
        changed = paths(self.i)[0]
        self.assertNotEqual(original, changed)
        self.manifest['agent_reach']['feedparser'] = '99.0.0'
        self.assertNotEqual(changed, paths(self.i)[0])

    def test_unmanaged_launcher_preserved_before_fetch(self):
        self.i.bin.mkdir(parents=True)
        name = 'opencli.cmd' if self.i.windows else 'opencli'
        target = self.i.bin / name
        target.write_text('personal tool')
        with patch.object(self.i, 'fetch') as fetch:
            with self.assertRaisesRegex(ValueError, 'Preserving unmanaged'):
                install(self.i)
        fetch.assert_not_called()
        self.assertEqual(target.read_text(), 'personal tool')

    def test_pins_reject_mutable_revision(self):
        self.i.spec('agent-reach')['revision'] = 'main'
        with self.assertRaisesRegex(ValueError, 'immutable'):
            paths(self.i)

    def test_wrong_provider_identity_fails_before_package_install(self):
        source = Path(self.tmp.name) / 'wrong-provider'
        source.mkdir()
        (source / 'pyproject.toml').write_text('[project]\nname="lookalike"\nversion="1.5.0"\n')
        with patch.object(self.i, 'fetch', return_value=source), patch('agentreach_runtime.run') as run:
            with self.assertRaisesRegex(ValueError, 'source identity'):
                install(self.i)
        run.assert_not_called()

    def test_failed_new_runtime_is_removed_for_retry(self):
        source = Path(self.tmp.name) / 'provider'
        source.mkdir()
        (source / 'pyproject.toml').write_text('[project]\nname="agent-reach"\nversion="1.5.0"\n')
        root, _, _ = paths(self.i)
        def fail(*args, **kwargs):
            root.mkdir(parents=True)
            (root / 'partial').write_text('incomplete')
            raise OSError('simulated interrupted install')
        with patch.object(self.i, 'fetch', return_value=source), patch('agentreach_runtime.run', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                install(self.i)
        self.assertFalse(root.exists())
        self.assertNotIn('agentreach', self.i.state['completed'])

    def test_skill_adapter_preserves_provider_and_personal_rules(self):
        source = Path(self.tmp.name) / 'provider'
        skill = source / 'agent_reach/skill'
        (skill / 'references').mkdir(parents=True)
        original = ('---\nname: agent-reach\ndescription: MUST USE for everything\n---\n'
                    '16 platforms, multiple backends each. **When this skill exists, use it for\n'
                    'these platforms — do not invent your own approach.**\n')
        (skill / 'SKILL_en.md').write_text(original)
        (skill / 'SKILL.md').write_text(original)
        (skill / 'references/social.md').write_text('Original provider reference')
        (source / 'LICENSE').write_text('Provider license')
        rules = self.home / '.codex/AGENTS.md'
        rules.parent.mkdir(parents=True)
        rules.write_text('Keep my rule.\n')
        install_skill(self.i, source)
        first = rules.read_text()
        install_skill(self.i, source)
        self.assertEqual(first, rules.read_text())
        self.assertIn('Keep my rule.', first)
        target = self.home / '.agents/skills/agent-reach'
        self.assertNotIn('MUST USE for everything', (target / 'SKILL.md').read_text())
        self.assertIn('overrides', (target / 'SKILL.md').read_text())
        self.assertEqual((skill / 'SKILL_en.md').read_text(), original)
        self.assertEqual((target / 'references/social.md').read_text(), 'Original provider reference')
        self.assertEqual((self.home / '.claude/skills/agent-reach').resolve(), target.resolve())
        self.assertFalse((self.home / '.claude.json').exists())
        self.assertFalse((self.home / '.agent-reach').exists())
        (target / 'references/social.md').write_text('Personal change')
        with self.assertRaisesRegex(ValueError, 'Preserving unmanaged'):
            install_skill(self.i, source)

    def test_windows_launcher_has_native_argv_and_scoped_environment(self):
        self.i.windows = True
        with patch.object(self.i, 'write') as write:
            write_launcher(self.i, 'agent-reach', [Path('C:/Users/Dev Name/python.exe'),
                '-B', '-c', 'from agent_reach.cli import main; main()'],
                search_path=Path('C:/Users/Dev Name/Scripts'), ci=True)
        text = write.call_args.args[1]
        self.assertIn('setlocal DisableDelayedExpansion', text)
        self.assertIn('set "PATH=' + str(Path('C:/Users/Dev Name/Scripts')) + ';%PATH%"', text)
        self.assertIn('set "CI=1"', text)
        self.assertIn('"from agent_reach.cli import main; main()" %*', text)
        self.assertIn('exit /b %errorlevel%', text)


if __name__ == '__main__':
    unittest.main()
