"""Run real PowerShell parsing/argument tests with simulated Windows prerequisites.

This is not evidence that installers or Windows runtimes execute on Windows.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
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
        executable = temp / 'fake python.exe'
        executable.write_text(f'''#!{sys.executable}
import json, os, pathlib, shutil, sys
args = sys.argv[1:]
with open(os.environ['SETUP_TEST_LOG'], 'a') as stream:
    stream.write(json.dumps(args) + '\\n')
if args[:2] == ['-m', 'venv']:
    target = pathlib.Path(args[2]) / 'Scripts/python.exe'
    target.parent.mkdir(parents=True)
    shutil.copy2(sys.argv[0], target)
elif args[:3] == ['-m', 'pip', 'install']:
    sys.exit(int(os.environ.get('SETUP_TEST_PIP_EXIT', '0')))
elif args and args[0].endswith('setup.py'):
    sys.exit(int(os.environ.get('SETUP_TEST_SETUP_EXIT', '0')))
elif args and args[0] == 'clone':
    target = pathlib.Path(args[2])
    target.mkdir(parents=True)
    (target / 'setup.py').write_text('# simulated downloaded repository')
    (target / 'requirements.txt').write_text('')
elif args and args[0] == '-C':
    print(os.environ.get('SETUP_TEST_ORIGIN', 'https://github.com/hiakki/ai_setup.git'))
''')
        executable.chmod(0o755)
        checkout = temp / 'repo & source with spaces'
        checkout.mkdir()
        (checkout / 'setup.py').write_text('# simulated setup boundary\n')
        (checkout / 'requirements.txt').write_text('')
        harness = temp / 'harness.ps1'
        harness.write_text('''$ErrorActionPreference = 'Stop'
. ./install.ps1
function Assert-NativeWindows { }
function Enable-SetupGit { return $env:SETUP_TEST_PYTHON }
function Install-SetupPython { return $env:SETUP_TEST_PYTHON }
function Find-SetupPython { return $env:SETUP_TEST_PYTHON }
function Install-SetupBuildTools { throw 'Selective skills install must not install C++ tools' }
function Set-SetupUserEnvironment { throw 'Isolated home must not persist user environment' }
$PSNativeCommandArgumentPassing = $env:SETUP_TEST_MODE
if ($env:SETUP_TEST_BOOTSTRAP -eq '1') { $script:EntryDirectory = Split-Path $env:SETUP_TEST_PYTHON -Parent }
Invoke-AISetup $env:SETUP_TEST_ACTION $env:SETUP_TEST_HOME 'skills,agents' $env:SETUP_TEST_CHECKOUT
''')
        env = dict(os.environ, SETUP_TEST_PYTHON=str(executable), SETUP_TEST_CHECKOUT=str(checkout))
        count = 0
        for mode in ('Standard', 'Legacy'):
            for action, pip_exit, setup_exit in (('install', 0, 0), ('install', 17, 0),
                                                ('install', 0, 23), ('plan', 0, 0), ('verify', 0, 23)):
                home = temp / f'home & spaces {count}'
                log = temp / f'log-{count}.jsonl'
                result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile',
                                         '-File', str(harness)], cwd=ROOT, env=dict(env,
                    SETUP_TEST_ACTION=action, SETUP_TEST_MODE=mode, SETUP_TEST_HOME=str(home),
                    SETUP_TEST_LOG=str(log), SETUP_TEST_PIP_EXIT=str(pip_exit),
                    SETUP_TEST_SETUP_EXIT=str(setup_exit)), text=True, capture_output=True, timeout=30)
                success = pip_exit == setup_exit == 0
                if (result.returncode == 0) != success:
                    raise AssertionError(f'{mode} {action} pip={pip_exit} setup={setup_exit}:\n'
                                         + result.stdout + result.stderr)
                calls = [json.loads(line) for line in log.read_text().splitlines()]
                if pip_exit:
                    assert not any(call[0].endswith('setup.py') for call in calls), calls
                else:
                    assert calls[-1] == [str(checkout / 'setup.py'), action, '--home', str(home),
                                        '--only', 'skills,agents'], calls
                if action != 'install':
                    assert not home.exists(), 'plan/verify unexpectedly mutated the installation home'
                print(f'PASS simulated: {mode} {action}; pip exit={pip_exit}, setup exit={setup_exit}')
                count += 1
            home = temp / f'bootstrap home & spaces {mode}'
            log = temp / f'bootstrap-{mode}.jsonl'
            result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(harness)],
                cwd=ROOT, env=dict(env, SETUP_TEST_ACTION='install', SETUP_TEST_MODE=mode,
                    SETUP_TEST_HOME=str(home), SETUP_TEST_LOG=str(log), SETUP_TEST_CHECKOUT='',
                    SETUP_TEST_BOOTSTRAP='1'), text=True, capture_output=True, timeout=30)
            assert result.returncode == 0, result.stdout + result.stderr
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            assert calls[0] == ['clone', 'https://github.com/hiakki/ai_setup.git',
                                str(home / '.local/share/ai-setup-repo')], calls
            print(f'PASS simulated: {mode} downloaded script clones into selected home')
        # Parse all syntax using PowerShell itself and reject accidentally restored WSL logic.
        source = (ROOT / 'install.ps1').read_text()
        assert 'wsl.exe' not in source and 'wsl --install' not in source
        parse = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-Command',
            "$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile("
            "(Join-Path (Get-Location) 'install.ps1'), [ref]$tokens, [ref]$errors) | Out-Null; "
            "if ($errors.Count) { $errors; exit 1 }"], cwd=ROOT, capture_output=True, text=True)
        assert parse.returncode == 0, parse.stdout + parse.stderr
        print('PASS: PowerShell syntax and native-default contract')
        # Mock only the registry boundary: exercise the real PATH merging twice.
        path_check = temp / 'path-check.ps1'
        path_check.write_text('''$ErrorActionPreference = 'Stop'
. ./install.ps1
$script:UserPath = 'C:\\Existing Tools;%USERPROFILE%\\bin'
$script:Writes = 0
function Get-SetupUserEnvironment { return $script:UserPath }
function Set-SetupUserEnvironment {
    param($Name, $Value)
    if ($Name -ne 'Path') { throw 'Unexpected registry setting' }
    $script:UserPath = $Value
    $script:Writes += 1
}
$env:PATH = 'C:\\Process Tools;C:\\Windows'
$target = 'C:\\Users\\Name & Spaces\\.local\\bin'
Add-SetupPath $target -Persist
Add-SetupPath ($target.ToUpper() + '\\') -Persist
if ($script:Writes -ne 1) { throw 'PATH persistence is not idempotent' }
if ($script:UserPath -ne ($target + ';C:\\Existing Tools;%USERPROFILE%\\bin')) { throw 'Existing user PATH was changed' }
if ($env:PATH -ne ($target + ';C:\\Process Tools;C:\\Windows')) { throw 'Existing process PATH was changed' }
Add-SetupPath 'C:\\Isolated Home\\.local\\bin'
if ($script:Writes -ne 1) { throw 'Isolated home persisted PATH' }
''')
        result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(path_check)],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
        print('PASS simulated: user/process PATH preservation, idempotence, and isolated home')


if __name__ == '__main__':
    main()
