"""Install checksum-pinned Entire release binaries from the original provider."""
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
        'Darwin': 'darwin', 'Linux': 'linux'}.get(platform.system())
    arch = {'arm64': 'arm64', 'aarch64': 'arm64',
            'x86_64': 'amd64', 'AMD64': 'amd64'}.get(platform.machine())
    target = f'{system}-{arch}'
    supported = ('darwin-amd64', 'darwin-arm64', 'linux-amd64',
                 'linux-arm64', 'windows-amd64')
    if target not in supported:
        raise ValueError('Entire supports macOS/Linux x64 or ARM64 and native Windows x64 in ai_setup')
    spec = installer.manifest['entire']
    version = spec['version']
    digest = spec['sha256'].get(target, '')
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('Entire requires a release version and SHA256 pin for this platform')
    os_name, arch_name = target.split('-', 1)
    archive = f'entire_{os_name}_{arch_name}' + ('.zip' if installer.windows else '.tar.gz')
    return {'version': version, 'target': target, 'sha256': digest, 'archive': archive}


def launchers(installer):
    suffix = '.exe' if installer.windows else ''
    return (installer.bin / ('entire' + suffix),
            installer.bin / ('git-remote-entire' + suffix))


def extract_binaries(archive, destination, windows=False):
    """Copy only the two expected regular binaries; ignore every other member."""
    names = ('entire.exe', 'git-remote-entire.exe') if windows else ('entire', 'git-remote-entire')
    destination.mkdir(parents=True, exist_ok=True)
    if windows:
        with zipfile.ZipFile(archive) as bundle:
            for name in names:
                entries = [entry for entry in bundle.infolist() if entry.filename == name]
                if (len(entries) != 1 or entries[0].is_dir()
                        or (entries[0].external_attr >> 16) & 0o170000 == 0o120000):
                    raise ValueError('Entire archive must contain exactly two regular CLI executables')
                with bundle.open(entries[0]) as source, (destination / name).open('wb') as output:
                    shutil.copyfileobj(source, output)
    else:
        with tarfile.open(archive, 'r:gz') as bundle:
            for name in names:
                entries = [entry for entry in bundle.getmembers() if entry.name == name]
                if len(entries) != 1 or not entries[0].isfile():
                    raise ValueError('Entire archive must contain exactly two regular CLI executables')
                with bundle.extractfile(entries[0]) as source, (destination / name).open('wb') as output:
                    shutil.copyfileobj(source, output)
                (destination / name).chmod(0o755)


def check_cli(binary, version, env):
    actual = capture([binary, '--version'], env=env, timeout=120)
    if not re.search(r'(?<![\d.])' + re.escape(version) + r'(?![\d.])', actual):
        raise ValueError(f'Entire executable does not report pinned version {version}')
    if not capture([binary, '--help'], env=env, timeout=120):
        raise ValueError('Entire executable returned no help output')


def install_guidance(installer):
    note = ('Entire is installed for Git-native Claude/Codex session provenance, but capture is '
            'disabled until a repository owner explicitly runs `entire enable`. Before enabling it, '
            'confirm that transcript retention is allowed, use an access-controlled private checkpoint '
            'remote, and review the provider security guide. Entire checkpoints may contain prompts, '
            'tool output, source content, MCP exchanges, screenshots or personal data even when secret '
            'redaction is enabled. Never send raw checkpoints to ai_setup, Agent Wiki or Hindsight. '
            'Promote only a reviewed, sanitized lesson with source repository and commit provenance. '
            'Run `entire status` to inspect capture and `entire disable --uninstall` to remove hooks.')
    for path in (installer.home / '.codex/AGENTS.md', installer.home / '.claude/CLAUDE.md'):
        installer.merge_text(path, note, 'entire')


def verify(installer):
    expected = release(installer)
    binary, helper = launchers(installer)
    for path in (binary, helper):
        installer.owned(path)
        if is_link(path) or not path.is_file():
            raise ValueError('Entire release is missing or modified; rerun --only entire')
    if installer.state.get('entire') != expected:
        raise ValueError('Entire release state differs from the manifest; rerun --only entire')
    check_cli(binary, expected['version'], installer.env)


def install(installer):
    expected = release(installer)
    binary, helper = launchers(installer)
    for path in (binary, helper):
        installer.owned(path)
        if is_link(path):
            raise ValueError(f'Preserving linked Entire launcher: {path}')
    if all(path.is_file() for path in (binary, helper)) and installer.state.get('entire') == expected:
        install_guidance(installer)
        verify(installer)
        return
    installer.bin.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.entire-install-', dir=installer.bin) as directory:
        temporary = Path(directory)
        archive = temporary / expected['archive']
        url = ('https://github.com/entireio/cli/releases/download/v' +
               expected['version'] + '/' + expected['archive'])
        download(url, archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('Entire release archive checksum mismatch; existing CLI was preserved')
        candidates = temporary / 'bin'
        extract_binaries(archive, candidates, installer.windows)
        check_cli(candidates / binary.name, expected['version'], installer.env)
        for candidate, target in zip((candidates / binary.name, candidates / helper.name),
                                     (binary, helper)):
            candidate.replace(target)
    for path in (binary, helper):
        installer.remember(path)
    installer.state['entire'] = expected
    installer.save()
    install_guidance(installer)
    print('Entire CLI installed. Session capture remains disabled in every repository until `entire enable`.')
