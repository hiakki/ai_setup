"""Fresh and upgrade lifecycle regressions without model calls or provider downloads."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from setup import Installer, venv_python
from runtime import install_codebase_memory, gstack, copy_gstack_skill, figma
from graphify_runtime import install as install_graphify


class PortableRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home with spaces'

    def test_figma_changed_pin_and_failed_legacy_upgrade_are_retryable(self):
        source = self.root / 'figma-provider'
        plugin = source / 'plugins/figma'
        plugin.mkdir(parents=True)
        (plugin / 'SKILL.md').write_text('New provider guidance')
        for windows in (False, True):
            i = Installer(self.home / str(windows), {'figma': {'repository': 'fixture/provider', 'revision': '2' * 40}})
            i.windows = windows
            i.state['completed'] = ['figma']
            i.state['sources']['openai-plugins'] = {'revision': '1' * 40}
            def fetched(spec):
                i.state['sources']['openai-plugins']['revision'] = spec['revision']
                return source
            with patch.object(i, 'fetch', side_effect=fetched) as fetch, \
                    patch('windows_runtime.command', return_value=['codex.exe']), \
                    patch('runtime.run', side_effect=ValueError('client failed')) as execute:
                with self.assertRaisesRegex(ValueError, 'client failed'):
                    figma(i)
                self.assertEqual(i.state['figma_revision'], '1' * 40)
                execute.side_effect = None
                figma(i)
                self.assertEqual(i.state['figma_revision'], '2' * 40)
                figma(i)
                self.assertEqual(fetch.call_count, 2)
                self.assertEqual(execute.call_count, 3)

    def test_graphify_first_install_and_repeat_use_final_interpreter(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'pyproject.toml').write_text('[project]\nname="graphifyy"\nversion="1.2.3"\n')
        i = Installer(self.home, {'graphify_version': '1.2.3', 'sources': [
            {'id': 'graphify', 'revision': '1' * 40}]})
        def execute(args, **kwargs):
            if '-m' in args and 'venv' in args:
                python = venv_python(args[-1])
                python.parent.mkdir(parents=True)
                python.touch()
        def check(installer, command, version):
            self.assertTrue(Path(command[0]).is_file(), command)
        with patch.object(i, 'fetch', return_value=source), \
                patch('graphify_runtime.run', side_effect=execute), \
                patch('graphify_runtime.check_cli', side_effect=check), \
                patch('graphify_runtime.install_skill'), patch('graphify_runtime.verify'):
            install_graphify(i)
            install_graphify(i)
        launcher = i.bin / ('graphify.cmd' if i.windows else 'graphify')
        self.assertNotIn('graphify-runtime-', launcher.read_text())

    def test_codebase_memory_upgrade_is_staged_and_preserves_local_changes(self):
        for windows in (False, True):
            i = Installer(self.home / str(windows), {'codebase_memory_version': '2.0.0',
                'codebase_memory_installer_sha256': hashlib.sha256(b'fixture').hexdigest(),
                'codebase_memory_windows_installer_sha256': hashlib.sha256(b'fixture').hexdigest(),
                'sources': [{'id': 'codebase-memory', 'revision': '1' * 40}]})
            i.windows = windows
            binary = i.bin / ('codebase-memory-mcp.exe' if windows else 'codebase-memory-mcp')
            binary.parent.mkdir(parents=True)
            binary.write_text('1.0.0')
            i.remember(binary)
            def execute(args, **kwargs):
                target = Path(next(str(x).split('=', 1)[1] for x in args if str(x).startswith('--dir=')))
                target.mkdir()
                (target / binary.name).write_text('2.0.0')
            with patch('runtime.download', side_effect=lambda url, path: path.write_bytes(b'fixture')) as download, \
                    patch('runtime.run', side_effect=execute), \
                    patch('runtime.capture', side_effect=lambda args, **kwargs: Path(args[0]).read_text()):
                install_codebase_memory(i)
                install_codebase_memory(i)
                self.assertEqual(download.call_count, 1)
                self.assertEqual(binary.read_text(), '2.0.0')
                binary.write_text('my custom binary')
                with self.assertRaisesRegex(ValueError, 'locally edited'):
                    install_codebase_memory(i)

    @unittest.skipIf(os.name == 'nt', 'Fixture symlinks need POSIX permissions')
    def test_gstack_materializes_internal_links_and_rejects_external_links(self):
        source, stage = self.root / 'source', self.root / 'stage'
        source.mkdir()
        stage.mkdir()
        (source / 'shared.md').write_text('Provider guidance')
        folder = stage / 'skill'
        folder.mkdir()
        link = folder / 'reference.md'
        link.symlink_to(source / 'shared.md')
        i = Installer(self.home, {'sources': []})
        target = i.home / '.agents/skills/example'
        copy_gstack_skill(i, folder, target, source, stage)
        self.assertEqual((target / 'reference.md').read_text(), 'Provider guidance')
        self.assertFalse((target / 'reference.md').is_symlink())
        link.unlink()
        outside = self.root / 'private.txt'
        outside.write_text('Do not import')
        link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'escapes provider'):
            copy_gstack_skill(i, folder, target, source, stage)

    @unittest.skipIf(os.name == 'nt', 'Fixture provider uses POSIX shell; Windows adapter covered separately')
    def test_gstack_generation_isolated_from_real_settings_and_repeats(self):
        source = self.root / 'gstack source'
        (source / 'bin').mkdir(parents=True)
        (source / '.agents/skills/gstack').mkdir(parents=True)
        (source / '.agents/skills/gstack/SKILL.md').write_text('---\nname: gstack\n---\nRouter\n')
        (source / 'setup').write_text('''#!/bin/bash
set -eu
mkdir -p "$HOME/.claude/skills/gstack-review" "$HOME/.codex/skills/gstack-review"
printf '{"hooks":"provider mutation"}' > "$HOME/.claude/settings.json"
printf '%s\\n' '---' 'name: review' '---' 'review guidance' > "$HOME/.claude/skills/gstack-review/SKILL.md"
cp "$HOME/.claude/skills/gstack-review/SKILL.md" "$HOME/.codex/skills/gstack-review/SKILL.md"
''')
        (source / 'bin/gstack-patch-names').write_text('#!/bin/sh\nexit 0\n')
        subprocess.run(['git', 'init', '-q', str(source)], check=True)
        subprocess.run(['git', '-C', str(source), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c',
            'user.email=fixture@example.invalid', 'commit', '--no-verify', '-qm', 'fixture'], check=True)
        i = Installer(self.home, {'sources': [{'id': 'gstack', 'revision': '1' * 40}]})
        settings = self.home / '.claude/settings.json'
        settings.parent.mkdir(parents=True)
        settings.write_text('{"hooks":"my hook"}')
        with patch.object(i, 'fetch', return_value=source), patch.object(i, 'verify', side_effect=AssertionError('aggregate verify too early')), \
                patch('runtime.shutil.which', return_value='/bin/true'):
            gstack(i)
            i.state['completed'].append('gstack')
            gstack(i)
            # Older installations recorded source provenance, not the completed
            # generation revision. A failed fetch/generation must remain retryable.
            del i.state['gstack_revision']
            i.state['sources']['gstack'] = {'revision': '1' * 40}
            i.manifest['sources'][0]['revision'] = '2' * 40
            def fetched(spec):
                i.state['sources']['gstack']['revision'] = spec['revision']
                return source
            with patch.object(i, 'fetch', side_effect=fetched), \
                    patch('runtime.run', side_effect=ValueError('generation failed')):
                with self.assertRaisesRegex(ValueError, 'generation failed'):
                    gstack(i)
            self.assertEqual(i.state['gstack_revision'], '1' * 40)
            gstack(i)
        self.assertEqual(settings.read_text(), '{"hooks":"my hook"}')
        self.assertIn('name: gstack-review', (self.home / '.agents/skills/gstack-review/SKILL.md').read_text())
        self.assertFalse((self.home / '.codex/skills/gstack-review').exists())
        self.assertEqual(i.state['gstack_revision'], '2' * 40)


if __name__ == '__main__':
    unittest.main()
