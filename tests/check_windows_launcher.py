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
    setting = 'SETUP_TEST_PLAN_EXIT' if args[1] == 'plan' else 'SETUP_TEST_SETUP_EXIT'
    sys.exit(int(os.environ.get(setting, '0')))
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
$selection = if ($env:SETUP_TEST_DEFAULT -eq '1') { $Only } elseif ($env:SETUP_TEST_SELECTION) { $env:SETUP_TEST_SELECTION } else { 'skills,agents' }
Invoke-AISetup $env:SETUP_TEST_ACTION $env:SETUP_TEST_HOME $selection $env:SETUP_TEST_CHECKOUT
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
                    assert not any(call[0].endswith('setup.py') and call[1] == 'install' for call in calls), calls
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
            # Exercise the script's actual default parameter and pass-through.
            log = temp / f'default-{mode}.jsonl'
            result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(harness)],
                cwd=ROOT, env=dict(env, SETUP_TEST_ACTION='plan', SETUP_TEST_MODE=mode,
                    SETUP_TEST_HOME=str(home), SETUP_TEST_LOG=str(log), SETUP_TEST_DEFAULT='1'),
                text=True, capture_output=True, timeout=30)
            assert result.returncode == 0, result.stdout + result.stderr
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            assert calls[-1] == [str(checkout / 'setup.py'), 'plan', '--home', str(home), '--only', 'all'], calls
            print(f'PASS simulated: {mode} default PowerShell selection forwards all components')
            for selection in ('context7', 'strix,skillui'):
                home = temp / f'optional home {mode} {selection}'
                log = temp / f'optional-{mode}-{selection}.jsonl'
                result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(harness)],
                    cwd=ROOT, env=dict(env, SETUP_TEST_ACTION='install', SETUP_TEST_MODE=mode,
                        SETUP_TEST_HOME=str(home), SETUP_TEST_LOG=str(log), SETUP_TEST_SELECTION=selection),
                    text=True, capture_output=True, timeout=30)
                assert result.returncode == 0, result.stdout + result.stderr
                calls = [json.loads(line) for line in log.read_text().splitlines()]
                assert calls[0] == [str(checkout / 'setup.py'), 'plan', '--home', str(home), '--only', selection], calls
                assert calls[-1] == [str(checkout / 'setup.py'), 'install', '--home', str(home), '--only', selection], calls
                print(f'PASS simulated: {mode} {selection} validates and forwards without C++ tools')
            log = temp / f'all-extras-{mode}.jsonl'
            result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(harness)],
                cwd=ROOT, env=dict(env, SETUP_TEST_ACTION='install', SETUP_TEST_MODE=mode,
                    SETUP_TEST_HOME=str(temp / 'isolated all'), SETUP_TEST_LOG=str(log),
                    SETUP_TEST_SELECTION=' all ,strix,skillui'), text=True, capture_output=True, timeout=30)
            assert result.returncode != 0 and 'requires the current user profile' in result.stderr, result.stderr
            assert not log.exists(), 'The Hermes home guard must run before prerequisite installation'
            print(f'PASS simulated: {mode} all plus optional tools retains Hermes profile guard')
        # Exercise the real PowerShell -> Python plan with only OS detection mocked.
        real_plan = temp / 'real-plan.ps1'
        real_plan.write_text('''$ErrorActionPreference = 'Stop'
. ./install.ps1
function Assert-NativeWindows { }
function Find-SetupPython { return $env:SETUP_REAL_PYTHON }
Invoke-AISetup $env:SETUP_PLAN_ACTION $env:SETUP_PLAN_HOME $env:SETUP_PLAN_ONLY (Get-Location).Path
''')
        plan_home = temp / 'plan home'
        for selection in ('all', 'all,strix,skillui', 'context7'):
            result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(real_plan)],
                cwd=ROOT, env=dict(os.environ, SETUP_REAL_PYTHON=sys.executable, SETUP_PLAN_HOME=str(plan_home),
                    SETUP_PLAN_ACTION='plan', SETUP_PLAN_ONLY=selection), capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, result.stdout + result.stderr
            components = next(line for line in result.stdout.splitlines() if line.startswith('Components:'))
            assert 'context7' in components, result.stdout
            if selection.startswith('all'):
                assert 'hermes' in components and 'runtime' in components, result.stdout
            assert ('strix' in components) == ('strix' in selection), result.stdout
            assert ('skillui' in components) == ('skillui' in selection), result.stdout
            assert not plan_home.exists(), 'Plan unexpectedly wrote to its target home'
            print(f'PASS: real PowerShell-to-Python {selection} plan expands defaults without writes')
        result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(real_plan)],
            cwd=ROOT, env=dict(os.environ, SETUP_REAL_PYTHON=sys.executable, SETUP_PLAN_HOME=str(plan_home),
                SETUP_PLAN_ACTION='install', SETUP_PLAN_ONLY='context77'), capture_output=True, text=True, timeout=30)
        assert result.returncode != 0 and 'Unknown component' in result.stderr, result.stderr
        assert not plan_home.exists(), 'Invalid selection unexpectedly mutated the target home'
        print('PASS: invalid selection fails before Windows bootstrap mutations')
        # A default profile with optional tools must still select the C++ runtime
        # prerequisite. Suppress all filesystem/registry writes to the real profile.
        runtime_guard = temp / 'runtime-guard.ps1'
        runtime_guard.write_text('''$ErrorActionPreference = 'Stop'
. ./install.ps1
function Assert-NativeWindows { }
function Find-SetupPython { return $env:SETUP_TEST_PYTHON }
function Install-SetupPython { return $env:SETUP_TEST_PYTHON }
function Enable-SetupGit { return $env:SETUP_TEST_PYTHON }
function New-Item { }
function Add-SetupPath { }
function Get-PSDrive { }
function Install-SetupBuildTools { throw 'BUILD_TOOLS_SELECTED' }
Invoke-AISetup 'install' ([Environment]::GetFolderPath('UserProfile')) ' all ,strix,skillui' $env:SETUP_TEST_CHECKOUT
''')
        result = subprocess.run([str(args.pwsh.resolve()), '-NoLogo', '-NoProfile', '-File', str(runtime_guard)],
            cwd=ROOT, env=dict(env, SETUP_TEST_LOG=str(temp / 'runtime-guard.jsonl')),
            capture_output=True, text=True, timeout=30)
        assert result.returncode != 0 and 'BUILD_TOOLS_SELECTED' in result.stderr, result.stdout + result.stderr
        print('PASS simulated: all plus optional tools retains C++ prerequisite selection')
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
