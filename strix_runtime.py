"""Optional Strix CLI from checksum-pinned upstream release binaries.

Install the native CLI only. Docker, sandbox images, provider credentials and
security scans are deliberately outside this installation workflow.
"""
import hashlib
from pathlib import Path
import platform
import re
import shutil
import tarfile
import tempfile
import zipfile

from runtime import download
from setup import capture, is_link


def release(installer):
    system = 'windows' if installer.windows else {
        'Darwin': 'macos', 'Linux': 'linux'}.get(platform.system())
    arch = {'arm64': 'arm64', 'aarch64': 'arm64',
            'x86_64': 'x86_64', 'AMD64': 'x86_64'}.get(platform.machine())
    target = f'{system}-{arch}'
    supported = ('macos-arm64', 'macos-x86_64', 'linux-arm64',
                 'linux-x86_64', 'windows-x86_64')
    if target not in supported:
        raise ValueError('Strix releases support macOS/Linux x64 or ARM64 and native Windows x64')
    spec = installer.manifest['strix']
    version = spec['version']
    digest = spec['sha256'].get(target, '')
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('Strix requires a release version and SHA256 pin for this platform')
    stem = f'strix-{version}-{target}'
    archive = stem + ('.zip' if installer.windows else '.tar.gz')
    return {'version': version, 'target': target, 'sha256': digest,
            'archive': archive, 'member': stem + ('.exe' if installer.windows else '')}


def launcher(installer):
    return installer.bin / ('strix.exe' if installer.windows else 'strix')


def extract_binary(archive, member, destination, windows=False):
    """Read exactly one regular member; never extract archive-controlled paths."""
    if windows:
        with zipfile.ZipFile(archive) as bundle:
            entries = [entry for entry in bundle.infolist() if entry.filename == member]
            if (len(entries) != 1 or entries[0].is_dir() or
                    (entries[0].external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Strix archive must contain exactly one regular CLI executable')
            with bundle.open(entries[0]) as source, destination.open('wb') as output:
                shutil.copyfileobj(source, output)
    else:
        with tarfile.open(archive, 'r:gz') as bundle:
            entries = [entry for entry in bundle.getmembers() if entry.name == member]
            if len(entries) != 1 or not entries[0].isfile():
                raise ValueError('Strix archive must contain exactly one regular CLI executable')
            with bundle.extractfile(entries[0]) as source, destination.open('wb') as output:
                shutil.copyfileobj(source, output)
    destination.chmod(0o755)


def check_cli(binary, version, env):
    actual = capture([binary, '--version'], env=env, timeout=120)
    if not re.search(r'(?<![\d.])' + re.escape(version) + r'(?![\d.])', actual):
        raise ValueError(f'Strix executable does not report pinned version {version}')
    if not capture([binary, '--help'], env=env, timeout=120):
        raise ValueError('Strix executable returned no help output')


def verify(installer):
    expected = release(installer)
    binary = launcher(installer)
    installer.owned(binary)
    if is_link(binary) or not binary.is_file() or installer.state.get('strix') != expected:
        raise ValueError('Strix release state is missing or differs from the manifest; rerun --only strix')
    check_cli(binary, expected['version'], installer.env)


def install_guidance(installer):
    spec = installer.spec('strix')
    source = installer.fetch(spec)
    for entry in spec['optional_skills']:
        installer.install_skill(source, entry)
    note = ('Strix is installed as an optional security tool. Read '
            '`~/.agents/skills/penetration-testing-with-strix/SKILL.md` and run `strix --help` '
            'before use. Installation does not authorize scanning, spending, source uploads or '
            'cloud actions. Establish explicit target scope and budget before a scan. Never '
            'fall back to managed cloud automatically. Local CLI scans may send source or '
            'findings to the configured LLM provider; Docker does not guarantee fully local data. '
            'Do not install/start Docker, pull sandbox images or enable CI scans without task authorization.')
    for path in (installer.home / '.codex/AGENTS.md', installer.home / '.claude/CLAUDE.md'):
        installer.merge_text(path, note, 'strix')


def install(installer):
    expected = release(installer)
    binary = launcher(installer)
    installer.owned(binary)
    if is_link(binary):
        raise ValueError(f'Preserving linked Strix launcher: {binary}')
    if binary.is_file() and installer.state.get('strix') == expected:
        install_guidance(installer)
        verify(installer)
        return
    binary.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.strix-install-', dir=binary.parent) as directory:
        temporary = Path(directory)
        archive = temporary / expected['archive']
        url = ('https://github.com/usestrix/strix/releases/download/v' +
               expected['version'] + '/' + expected['archive'])
        download(url, archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('Strix release archive checksum mismatch; existing CLI was preserved')
        candidate = temporary / binary.name
        extract_binary(archive, expected['member'], candidate, installer.windows)
        # Validate before publishing so a broken download cannot replace a working CLI.
        check_cli(candidate, expected['version'], installer.env)
        candidate.replace(binary)
    installer.remember(binary)
    installer.state['strix'] = expected
    installer.save()
    install_guidance(installer)
    print('Strix CLI installed. No Docker setup, sandbox image download, credentials or scans were run. '
          'Local scans need a running Docker Linux-container backend and a configured model; '
          'managed cloud scans use separate account access.')
