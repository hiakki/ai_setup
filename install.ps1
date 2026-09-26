# Native Windows entry point. Git Bash is an auxiliary tool, not a Linux VM.
[CmdletBinding()]
param(
    [ValidateSet('install', 'plan', 'verify')][string]$Action = 'install',
    [string]$HomeDirectory = [Environment]::GetFolderPath('UserProfile'),
    # Defaults include Context7 and Hermes; opt in with -Only 'all,strix,skillui'.
    # setup.py owns the component list and expands all to the default components.
    [string]$Only = 'all',
    [string]$RepositoryDirectory = ''
)
$ErrorActionPreference = 'Stop'
$script:EntryDirectory = $PSScriptRoot

function Assert-NativeWindows {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        throw 'install.ps1 requires native Windows. On macOS/Linux use install.sh.'
    }
    if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') {
        throw 'The native installer currently requires Windows x64; ARM64 is not yet verified.'
    }
}

function Invoke-CheckedNative {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable failed (exit $LASTEXITCODE). Fix the reported cause and rerun." }
}

function Get-SetupUserEnvironment {
    param([string]$Name)
    return [Environment]::GetEnvironmentVariable($Name, 'User')
}

function Set-SetupUserEnvironment {
    param([string]$Name, [string]$Value)
    [Environment]::SetEnvironmentVariable($Name, $Value, 'User')
}

function Add-SetupPath {
    param([string]$Directory, [switch]$Persist)
    # Keep existing entries verbatim, including expandable variables and ordering.
    $directoryKey = $Directory.TrimEnd('\', '/')
    $processEntries = @($env:PATH -split ';' | ForEach-Object {
        [Environment]::ExpandEnvironmentVariables($_.Trim().Trim('"')).TrimEnd('\', '/')
    })
    if ($directoryKey -notin $processEntries) { $env:PATH = $Directory + ';' + $env:PATH }
    if ($Persist) {
        $userPath = Get-SetupUserEnvironment 'Path'
        $userEntries = @($userPath -split ';' | ForEach-Object {
            [Environment]::ExpandEnvironmentVariables($_.Trim().Trim('"')).TrimEnd('\', '/')
        })
        if ($directoryKey -notin $userEntries) {
            $updatedPath = $Directory
            if ($userPath) { $updatedPath += ';' + $userPath }
            Set-SetupUserEnvironment 'Path' $updatedPath
        }
    }
}

function Get-VerifiedDownload {
    param([string]$Uri, [string]$Destination, [string]$Sha256 = '', [string]$Publisher = '')
    if (-not (Test-Path -LiteralPath $Destination)) {
        $temporary = "$Destination.download"
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing -Uri $Uri -OutFile $temporary
        Move-Item -LiteralPath $temporary -Destination $Destination -Force
    }
    if ($Sha256 -and (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash -ne $Sha256) {
        throw "Checksum mismatch: $Destination. Remove that download and rerun."
    }
    if ($Publisher) {
        $signature = Get-AuthenticodeSignature -LiteralPath $Destination
        if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch $Publisher) {
            throw "Untrusted publisher signature: $Destination"
        }
    }
    return $Destination
}

function Invoke-InstallerProcess {
    param([string]$Executable, [string[]]$Arguments, [switch]$Elevated)
    # Start-Process joins ArgumentList; quote values explicitly for Windows CRT.
    $quoted = foreach ($argument in $Arguments) {
        '"' + [regex]::Replace([regex]::Replace($argument, '(\\*)"', '$1$1\"'), '(\\+)$', '$1$1') + '"'
    }
    $options = @{ FilePath = $Executable; ArgumentList = ($quoted -join ' '); Wait = $true; PassThru = $true }
    if ($Elevated) { $options.Verb = 'RunAs' }
    $process = Start-Process @options
    if ($process.ExitCode -eq 3010) {
        throw 'A prerequisite installed successfully but Windows requires a restart. Restart Windows, then rerun install.ps1.'
    }
    if ($process.ExitCode -ne 0) { throw "Prerequisite installer failed (exit $($process.ExitCode)): $Executable" }
}

function Find-SetupPython {
    param([string]$BootstrapDirectory)
    $candidates = @((Join-Path $BootstrapDirectory 'python/python.exe'))
    foreach ($name in @('python.exe', 'python3.exe', 'py.exe')) {
        $command = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($command) { $candidates += $command.Source }
    }
    foreach ($candidate in $candidates) {
        if (-not (Test-Path -LiteralPath $candidate) -or $candidate -match '\\WindowsApps\\') { continue }
        $output = & $candidate -c 'import sys; print(sys.executable) if (3,12) <= sys.version_info < (3,14) else sys.exit(1)' 2>$null
        if ($LASTEXITCODE -eq 0 -and $output) { return [string]($output | Select-Object -Last 1) }
    }
    return $null
}

function Install-SetupPython {
    param([string]$BootstrapDirectory)
    $python = Find-SetupPython $BootstrapDirectory
    if ($python) { return $python }
    $installer = Get-VerifiedDownload 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' (Join-Path $BootstrapDirectory 'python-3.12.10-amd64.exe') '67b5635e80ea51072b87941312d00ec8927c4db9ba18938f7ad2d27b328b95fb'
    Invoke-InstallerProcess $installer @('/quiet', 'InstallAllUsers=0', 'Include_launcher=0', 'Include_test=0', 'Include_doc=0', 'PrependPath=0', ('TargetDir=' + (Join-Path $BootstrapDirectory 'python')))
    $python = Find-SetupPython $BootstrapDirectory
    if (-not $python) { throw 'Python installation did not produce a usable Python 3.12-3.13 interpreter.' }
    return $python
}

function Enable-SetupGit {
    param([string]$BootstrapDirectory, [switch]$Persist)
    $gitRoot = Join-Path $BootstrapDirectory 'git'
    $roots = @($gitRoot)
    $existing = Get-Command git.exe -CommandType Application -ErrorAction SilentlyContinue
    if ($existing) { $roots += Split-Path (Split-Path $existing.Source -Parent) -Parent }
    foreach ($root in $roots) {
        if ((Test-Path -LiteralPath (Join-Path $root 'cmd/git.exe')) -and (Test-Path -LiteralPath (Join-Path $root 'bin/bash.exe'))) {
            $gitRoot = $root
            break
        }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $gitRoot 'bin/bash.exe'))) {
        $portable = Get-VerifiedDownload 'https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/PortableGit-2.55.0.5-64-bit.7z.exe' (Join-Path $BootstrapDirectory 'PortableGit-2.55.0.5-64-bit.7z.exe') '5aa8a20f6e9abb2c755f0e73c91c687701a46b309ad84a0ca6509380fa4ae290'
        Invoke-InstallerProcess $portable @('-y', ('-o' + $gitRoot))
    }
    Add-SetupPath (Join-Path $gitRoot 'bin') -Persist:$Persist
    Add-SetupPath (Join-Path $gitRoot 'cmd') -Persist:$Persist
    if (-not $env:CLAUDE_CODE_GIT_BASH_PATH) { $env:CLAUDE_CODE_GIT_BASH_PATH = Join-Path $gitRoot 'bin/bash.exe' }
    if ($Persist -and -not (Get-SetupUserEnvironment 'CLAUDE_CODE_GIT_BASH_PATH')) {
        Set-SetupUserEnvironment 'CLAUDE_CODE_GIT_BASH_PATH' $env:CLAUDE_CODE_GIT_BASH_PATH
    }
    return Join-Path $gitRoot 'cmd/git.exe'
}

function Install-SetupBuildTools {
    param([string]$BootstrapDirectory)
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
    if (Test-Path -LiteralPath $vswhere) {
        $found = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        if ($LASTEXITCODE -eq 0 -and $found) { return }
    }
    Write-Host 'Graft needs Microsoft C++ build tools. Windows will request administrator approval for this system prerequisite.'
    $installer = Get-VerifiedDownload 'https://aka.ms/vs/17/release/vs_buildtools.exe' (Join-Path $BootstrapDirectory 'vs_buildtools.exe') -Publisher 'O=Microsoft Corporation'
    Invoke-InstallerProcess $installer @('--wait', '--passive', '--norestart', '--add', 'Microsoft.VisualStudio.Workload.VCTools', '--includeRecommended') -Elevated
}

function Invoke-AISetup {
    param([string]$SetupAction, [string]$SetupHome, [string]$SetupOnly, [string]$Checkout)
    Assert-NativeWindows
    $env:PYTHONUTF8 = '1'
    $SetupHome = [IO.Path]::GetFullPath($SetupHome)
    $selected = if ($SetupOnly) { $SetupOnly } else { 'all' }
    $components = @($selected.Split(',') | ForEach-Object { $_.Trim() })
    $currentUserHome = [IO.Path]::GetFullPath([Environment]::GetFolderPath('UserProfile'))
    if ($SetupAction -eq 'install' -and ('all' -in $components -or 'hermes' -in $components) -and $SetupHome -ne $currentUserHome) {
        throw 'The full setup includes Hermes and requires the current user profile. Omit -HomeDirectory, or use -Only with components excluding hermes for an isolated test.'
    }
    $bootstrap = Join-Path $SetupHome '.local/share/ai-setup/bootstrap'
    if (-not $Checkout -and $script:EntryDirectory -and (Test-Path -LiteralPath (Join-Path $script:EntryDirectory 'setup.py'))) {
        $Checkout = $script:EntryDirectory
    }
    $hasCheckout = $Checkout -and (Test-Path -LiteralPath (Join-Path $Checkout 'setup.py'))
    $validatedSelection = $false
    if ($SetupAction -eq 'install' -and $hasCheckout) {
        $existingPython = Find-SetupPython $bootstrap
        if ($existingPython) {
            Invoke-CheckedNative $existingPython @((Join-Path $Checkout 'setup.py'), 'plan', '--home', $SetupHome, '--only', $selected) | Out-Null
            $validatedSelection = $true
        }
    }
    if ($SetupAction -ne 'install') {
        if (-not $hasCheckout) { throw 'plan/verify require a local repository checkout. Run install first.' }
        $python = Join-Path $SetupHome '.local/share/ai-setup/venv/Scripts/python.exe'
        if (-not (Test-Path -LiteralPath $python)) { $python = Find-SetupPython $bootstrap }
        if (-not $python) { throw 'Python 3.12-3.13 is required to preview or verify; install first.' }
    } else {
        $needsRuntime = 'all' -in $components -or 'runtime' -in $components
        $drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($SetupHome).TrimEnd('\').TrimEnd(':')) -ErrorAction SilentlyContinue
        if ($needsRuntime -and $drive -and $drive.Free -lt 20GB -and -not (Test-Path -LiteralPath (Join-Path $SetupHome '.local/state/ai-setup/state.json'))) {
            throw 'A fresh native setup needs at least 20 GiB free for build tools, packages, and browsers.'
        }
        New-Item -ItemType Directory -Path $bootstrap -Force | Out-Null
        $persist = $SetupHome -eq [IO.Path]::GetFullPath([Environment]::GetFolderPath('UserProfile'))
        $git = Enable-SetupGit $bootstrap -Persist:$persist
        Add-SetupPath (Join-Path $SetupHome '.local/bin') -Persist:$persist
        if (-not $hasCheckout) {
            if (-not $Checkout) { $Checkout = Join-Path $SetupHome '.local/share/ai-setup-repo' }
            if (Test-Path -LiteralPath $Checkout) {
                $origin = & $git -C $Checkout remote get-url origin
                if ($LASTEXITCODE -ne 0 -or $origin -notin @('https://github.com/hiakki/ai_setup.git', 'git@github.com:hiakki/ai_setup.git')) {
                    throw "Preserving unrelated setup directory: $Checkout"
                }
            } else { Invoke-CheckedNative $git @('clone', 'https://github.com/hiakki/ai_setup.git', $Checkout) }
        }
        if (-not (Test-Path -LiteralPath (Join-Path $Checkout 'setup.py'))) { throw "Incomplete setup checkout: $Checkout" }
        $basePython = Install-SetupPython $bootstrap
        if (-not $validatedSelection) {
            Invoke-CheckedNative $basePython @((Join-Path $Checkout 'setup.py'), 'plan', '--home', $SetupHome, '--only', $selected) | Out-Null
        }
        $env:npm_config_python = $basePython
        $env:PYTHON = $basePython
        if ($needsRuntime) { Install-SetupBuildTools $bootstrap }
        $venv = Join-Path $SetupHome '.local/share/ai-setup/venv'
        $python = Join-Path $venv 'Scripts/python.exe'
        if (-not (Test-Path -LiteralPath $python)) { Invoke-CheckedNative $basePython @('-m', 'venv', $venv) }
        Invoke-CheckedNative $python @('-m', 'pip', 'install', '--disable-pip-version-check', '-r', (Join-Path $Checkout 'requirements.txt'))
    }
    $arguments = @((Join-Path $Checkout 'setup.py'), $SetupAction, '--home', $SetupHome)
    $arguments += @('--only', $selected)
    Invoke-CheckedNative $python $arguments
}

# Dot-sourcing loads functions for focused tests without installing anything.
if ($MyInvocation.InvocationName -ne '.') {
    Invoke-AISetup $Action $HomeDirectory $Only $RepositoryDirectory
}
