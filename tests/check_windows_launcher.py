"""Optional PowerShell/native-argument check; does not claim to run Windows or WSL."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pwsh', required=True, type=Path)
    args = parser.parse_args()
    work = ROOT / '.work'
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=work) as temp:
        temp = Path(temp)
        home = temp / 'home with spaces'
        repository = home / '.local/share/ai-setup-repo'
        repository.mkdir(parents=True)
        marker = temp / 'installed'
        (repository / 'install.sh').write_text('printf installed > "$SETUP_TEST_MARKER"\n')
        binaries = temp / 'bin'
        binaries.mkdir()
        # A native executable boundary catches quoting differences which a
        # PowerShell function mock would hide. Only the fixture shell is run.
        (binaries / 'wsl.exe').write_text('''#!/bin/bash
set -eu
[[ "$1" == -d && "$2" == Debian && "$3" == -- ]] || exit 91
shift 3
[[ "$1" == bash && "$2" == -lc && "$#" == 3 ]] || exit 92
if [[ "$3" == 'command -v bash >/dev/null' ]]; then
  exit "${SETUP_TEST_WSL_EXIT:-0}"
fi
if [[ "${SETUP_TEST_INSTALL_EXIT:-0}" != 0 ]]; then exit "$SETUP_TEST_INSTALL_EXIT"; fi
exec /bin/bash -c "$3"
''')
        (binaries / 'git').write_text('''#!/bin/bash
set -eu
[[ "$1" == -C && "$2" == "$HOME/.local/share/ai-setup-repo" ]] || exit 93
printf '%s\n' https://github.com/hiakki/ai_setup.git
''')
        for executable in binaries.iterdir():
            executable.chmod(0o755)
        env = dict(os.environ, HOME=str(home), SETUP_TEST_MARKER=str(marker),
                   PATH=str(binaries) + os.pathsep + os.environ['PATH'])
        for mode in ('Standard', 'Legacy'):
            command = [str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-Command',
                       f"$PSNativeCommandArgumentPassing='{mode}'; & ./install.ps1 -Distribution Debian"]
            for wsl_exit, install_exit in ((0, 0), (17, 0), (0, 23)):
                marker.unlink(missing_ok=True)
                result = subprocess.run(command, cwd=ROOT, env=dict(env,
                    SETUP_TEST_WSL_EXIT=str(wsl_exit), SETUP_TEST_INSTALL_EXIT=str(install_exit)),
                    text=True, capture_output=True, timeout=30)
                expected_success = wsl_exit == install_exit == 0
                if (result.returncode == 0) != expected_success or marker.exists() != expected_success:
                    raise AssertionError(f'{mode}, WSL={wsl_exit}, install={install_exit}:\n'
                                         + result.stdout + result.stderr)
                print(f'PASS: {mode} argument handling; WSL exit={wsl_exit}, install exit={install_exit}')


if __name__ == '__main__':
    main()
