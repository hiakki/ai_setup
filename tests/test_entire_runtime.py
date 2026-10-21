import hashlib
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup import Installer, ROOT
from entire_runtime import extract_binaries, install, launchers, release, verify


class EntireRuntimeTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.work').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / '.work')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.installer = Installer(self.directory / 'home with spaces', {
            'entire': {'version': '0.11.4', 'sha256': {
                'darwin-arm64': '0' * 64, 'linux-amd64': '0' * 64,
                'windows-amd64': '0' * 64}}})
        self.installer.windows = False
        self.addCleanup(patch.stopall)
        patch('entire_runtime.platform.system', return_value='Darwin').start()
        patch('entire_runtime.platform.machine', return_value='arm64').start()
        patch('entire_runtime.install_guidance').start()

    def archive(self, body):
        path = self.directory / 'release.tar.gz'
        with tarfile.open(path, 'w:gz') as bundle:
            for name in ('entire', 'git-remote-entire'):
                entry = tarfile.TarInfo(name)
                entry.mode = 0o755
                entry.size = len(body)
                bundle.addfile(entry, io.BytesIO(body))
        self.installer.manifest['entire']['sha256']['darwin-arm64'] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def test_release_matrix_includes_native_windows_without_wsl(self):
        self.installer.windows = True
        with patch('entire_runtime.platform.machine', return_value='AMD64'):
            selected = release(self.installer)
        self.assertEqual(selected['target'], 'windows-amd64')
        self.assertEqual(selected['archive'], 'entire_windows_amd64.zip')
        self.assertEqual([p.name for p in launchers(self.installer)],
                         ['entire.exe', 'git-remote-entire.exe'])

    def test_archive_ignores_paths_and_rejects_links_or_missing_helpers(self):
        unsafe = self.directory / 'unsafe.tar.gz'
        with tarfile.open(unsafe, 'w:gz') as bundle:
            entire = tarfile.TarInfo('entire')
            entire.type = tarfile.SYMTYPE
            entire.linkname = '/tmp/elsewhere'
            bundle.addfile(entire)
            helper = tarfile.TarInfo('git-remote-entire')
            helper.size = 1
            bundle.addfile(helper, io.BytesIO(b'x'))
        with self.assertRaisesRegex(ValueError, 'regular CLI'):
            extract_binaries(unsafe, self.directory / 'bin')

        archive = self.directory / 'release.zip'
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr('../escape', 'unwanted')
            bundle.writestr('entire.exe', 'entire')
            bundle.writestr('git-remote-entire.exe', 'helper')
        output = self.directory / 'windows-bin'
        extract_binaries(archive, output, windows=True)
        self.assertEqual((output / 'entire.exe').read_text(), 'entire')
        self.assertFalse((self.directory / 'escape').exists())

    def test_checksum_failure_preserves_existing_binaries(self):
        archive = self.archive(b'bad')
        self.installer.manifest['entire']['sha256']['darwin-arm64'] = '0' * 64
        for path in launchers(self.installer):
            self.installer.write(path, 'old')
        with patch('entire_runtime.download', side_effect=lambda url, dst: dst.write_bytes(archive.read_bytes())), \
                patch('entire_runtime.check_cli') as check:
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                install(self.installer)
        self.assertEqual([p.read_text() for p in launchers(self.installer)], ['old', 'old'])
        check.assert_not_called()

    def test_install_rerun_and_verify_real_fixture(self):
        body = b'#!/bin/sh\ncase "$1" in --version) echo "entire 0.11.4";; --help) echo help;; *) exit 2;; esac\n'
        archive = self.archive(body)
        with patch('entire_runtime.download', side_effect=lambda url, dst: dst.write_bytes(archive.read_bytes())) as download:
            install(self.installer)
            install(self.installer)
            verify(self.installer)
        self.assertEqual(download.call_count, 1)
        self.assertEqual(self.installer.state['entire']['version'], '0.11.4')


if __name__ == '__main__':
    unittest.main()
