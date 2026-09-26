import hashlib
import io
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT
from strix_runtime import extract_binary, install, install_guidance, launcher, release, verify


class StrixRuntimeTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.installer = Installer(self.directory / 'home with spaces', {
            'strix': {'version': '1.6.2', 'sha256': {
                'macos-arm64': '0' * 64, 'linux-x86_64': '0' * 64,
                'windows-x86_64': '0' * 64}}})
        self.installer.windows = False
        self.addCleanup(patch.stopall)
        patch('strix_runtime.platform.system', return_value='Darwin').start()
        patch('strix_runtime.platform.machine', return_value='arm64').start()
        self.guidance = patch('strix_runtime.install_guidance').start()

    def archive(self, body=b'fixture', *, version='1.6.2'):
        path = self.directory / 'release.tar.gz'
        with tarfile.open(path, 'w:gz') as bundle:
            entry = tarfile.TarInfo(f'strix-{version}-macos-arm64')
            entry.size = len(body)
            bundle.addfile(entry, io.BytesIO(body))
        self.installer.manifest['strix']['sha256']['macos-arm64'] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def downloader(self, archive):
        return lambda url, destination: destination.write_bytes(archive.read_bytes())

    def test_native_windows_release_needs_no_wsl_or_python_environment(self):
        self.installer.windows = True
        with patch('strix_runtime.platform.machine', return_value='AMD64'):
            selected = release(self.installer)
        self.assertEqual(selected['target'], 'windows-x86_64')
        self.assertEqual(selected['archive'], 'strix-1.6.2-windows-x86_64.zip')
        self.assertEqual(selected['member'], 'strix-1.6.2-windows-x86_64.exe')
        self.assertEqual(launcher(self.installer).name, 'strix.exe')

    def test_unsupported_platform_rejected_before_download(self):
        self.installer.windows = True
        with patch('strix_runtime.download') as download:
            with self.assertRaisesRegex(ValueError, 'native Windows x64'):
                install(self.installer)
            download.assert_not_called()

    def test_checksum_failure_preserves_previous_managed_binary(self):
        archive = self.archive()
        self.installer.manifest['strix']['sha256']['macos-arm64'] = '0' * 64
        target = launcher(self.installer)
        self.installer.write(target, 'old binary')
        with patch('strix_runtime.download', side_effect=self.downloader(archive)), \
                patch('strix_runtime.check_cli') as check:
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                install(self.installer)
        self.assertEqual(target.read_text(), 'old binary')
        check.assert_not_called()

    def test_invalid_cli_preserves_previous_binary(self):
        archive = self.archive()
        target = launcher(self.installer)
        self.installer.write(target, 'old binary')
        with patch('strix_runtime.download', side_effect=self.downloader(archive)), \
                patch('strix_runtime.check_cli', side_effect=ValueError('bad version')):
            with self.assertRaisesRegex(ValueError, 'bad version'):
                install(self.installer)
        self.assertEqual(target.read_text(), 'old binary')

    def test_unmanaged_binary_preserved_without_downloading(self):
        target = launcher(self.installer)
        target.parent.mkdir(parents=True)
        target.write_text('operator binary')
        with patch('strix_runtime.download') as download:
            with self.assertRaisesRegex(ValueError, 'Preserving unmanaged'):
                install(self.installer)
            download.assert_not_called()

    def test_tar_links_and_duplicate_members_rejected(self):
        name = 'strix-1.6.2-macos-arm64'
        archive = self.directory / 'unsafe.tar.gz'
        for kind in ('symlink', 'duplicate'):
            with self.subTest(kind=kind):
                with tarfile.open(archive, 'w:gz') as bundle:
                    entry = tarfile.TarInfo(name)
                    if kind == 'symlink':
                        entry.type = tarfile.SYMTYPE
                        entry.linkname = '/tmp/unrelated'
                    bundle.addfile(entry)
                    if kind == 'duplicate':
                        bundle.addfile(entry)
                with self.assertRaisesRegex(ValueError, 'regular CLI'):
                    extract_binary(archive, name, self.directory / 'output')

    def test_zip_reads_only_expected_binary_without_extracting_paths(self):
        archive = self.directory / 'release.zip'
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr('../escape', 'unwanted')
            bundle.writestr('strix.exe', 'fixture executable')
        output = self.directory / 'output.exe'
        extract_binary(archive, 'strix.exe', output, windows=True)
        self.assertEqual(output.read_text(), 'fixture executable')
        self.assertFalse((self.directory.parent / 'escape').exists())

    def test_guidance_installs_all_optional_skills_and_bounded_routing(self):
        source = self.directory / 'provider'
        entry = {'path': 'skills/penetration-testing-with-strix',
                 'name': 'penetration-testing-with-strix'}
        folder = source / entry['path']
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text('---\nname: penetration-testing-with-strix\n'
                                       'description: Security fixture\n---\nFixture\n')
        self.installer.manifest['sources'] = [{'id': 'strix', 'optional_skills': [entry]}]
        with patch.object(self.installer, 'fetch', return_value=source):
            install_guidance(self.installer)
            install_guidance(self.installer)
        self.assertTrue((self.installer.home / '.agents/skills' / entry['name'] / 'SKILL.md').is_file())
        for path in (self.installer.home / '.codex/AGENTS.md', self.installer.home / '.claude/CLAUDE.md'):
            text = path.read_text()
            self.assertEqual(text.count('<!-- ai-setup:strix:start -->'), 1)
            self.assertIn('explicit target scope and budget', text)
            self.assertIn('Never fall back to managed cloud automatically', text)

    @unittest.skipIf(os.name == 'nt', 'POSIX executable fixture; Windows artifact selection tested separately')
    def test_install_and_repeat_run_actual_help_version_without_scan(self):
        archive = self.archive(b'#!/bin/sh\ncase "$1" in\n--version) echo "Strix 1.6.2";;\n--help) echo "Strix help";;\n*) exit 91;;\nesac\n')
        with patch('strix_runtime.download', side_effect=self.downloader(archive)) as download:
            install(self.installer)
            install(self.installer)
            verify(self.installer)
        self.assertEqual(download.call_count, 1)
        self.assertEqual(self.installer.state['strix']['version'], '1.6.2')
        launcher(self.installer).write_text('operator change')
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            verify(self.installer)


if __name__ == '__main__':
    unittest.main()
