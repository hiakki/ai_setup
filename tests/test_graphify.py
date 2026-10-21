import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from setup import Installer, ROOT


class GraphifyTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home'

    def test_provider_pins_and_ponytail_skill_set(self):
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        sources = {entry['id']: entry for entry in manifest['sources']}
        self.assertEqual(sources['graphify']['url'], 'https://github.com/Graphify-Labs/graphify.git')
        self.assertRegex(sources['graphify']['revision'], r'^[0-9a-f]{40}$')
        self.assertEqual(manifest['graphify_version'], '0.9.89')
        self.assertEqual(
            {entry['name'] for entry in sources['ponytail']['skills']},
            {'ponytail', 'ponytail-audit', 'ponytail-debt', 'ponytail-gain',
             'ponytail-help', 'ponytail-review'},
        )

    def test_package_version_rejects_lookalike_provider(self):
        from graphify_runtime import package_version
        source = Path(self.tmp.name) / 'source'
        source.mkdir()
        (source / 'pyproject.toml').write_text(
            '[project]\nname = "graphifyy"\nversion = "0.9.89"\n', encoding='utf-8')
        self.assertEqual(package_version(source), '0.9.89')
        (source / 'pyproject.toml').write_text(
            '[project]\nname = "graphify"\nversion = "0.9.89"\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'package name changed'):
            package_version(source)

    def test_provider_generates_global_skill_without_hooks_or_mcp(self):
        from graphify_runtime import install_skill
        installer = Installer(self.home, {'graphify_version': '0.9.89'})
        installer.state_dir.mkdir(parents=True)
        calls = []

        def provider_run(args, **kwargs):
            calls.append(list(map(str, args)))
            stage = Path(kwargs['env']['HOME']) / '.agents/skills/graphify'
            (stage / 'references').mkdir(parents=True)
            (stage / 'SKILL.md').write_text(
                '---\nname: graphify\ndescription: Mixed graph\n---\nUse references.\n',
                encoding='utf-8')
            (stage / 'references/extraction.md').write_text('Provider reference\n', encoding='utf-8')

        with patch('graphify_runtime.run', side_effect=provider_run):
            install_skill(installer, [Path('/provider/python'), '-m', 'graphify'])

        self.assertEqual(calls, [['/provider/python', '-m', 'graphify', 'install', '--platform', 'agents']])
        skill = self.home / '.agents/skills/graphify'
        self.assertTrue((skill / 'SKILL.md').is_file())
        self.assertEqual((skill / 'references/extraction.md').read_text(), 'Provider reference\n')
        self.assertEqual((self.home / '.claude/skills/graphify').resolve(), skill.resolve())
        self.assertFalse((self.home / '.codex/config.toml').exists())
        self.assertFalse((self.home / '.claude/settings.json').exists())


if __name__ == '__main__':
    unittest.main()
