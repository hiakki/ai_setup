# Windows entry point. The complete environment lives inside WSL2, under its Linux user.
[CmdletBinding()]
param([string]$Distribution = 'Ubuntu')
$ErrorActionPreference = 'Stop'
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'WSL is unavailable. In Administrator PowerShell run: wsl --install -d Ubuntu; reboot and create your Linux user, then rerun this script.'
}
& wsl.exe -d $Distribution -- bash -lc 'command -v bash >/dev/null'
if ($LASTEXITCODE -ne 0) {
    throw "Initialize WSL2 first: wsl --install -d $Distribution. Reboot if requested, launch the distribution and create your Linux user, then rerun."
}
# Windows PowerShell's legacy native-argument handling strips embedded quotes.
# Encode this fixed script so both PowerShell 5.1 and 7 pass one intact argument.
# No Windows paths, user input or credentials are interpolated into shell code.
$setupScript = @'
set -euo pipefail
command -v git >/dev/null || { sudo apt-get update && sudo apt-get install -y git; }
setup_repo="$HOME/.local/share/ai-setup-repo"
if [ ! -e "$setup_repo" ]; then
  git clone https://github.com/hiakki/ai_setup.git "$setup_repo"
elif [ "$(git -C "$setup_repo" remote get-url origin)" != https://github.com/hiakki/ai_setup.git ]; then
  echo "Preserving unrelated setup directory" >&2
  exit 1
fi
bash "$setup_repo/install.sh"
'@
$setupPayload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($setupScript.Replace("`r", '')))
& wsl.exe -d $Distribution -- bash -lc "set -o pipefail; echo $setupPayload | base64 -d | bash"
if ($LASTEXITCODE -ne 0) { throw "ai_setup failed inside WSL ($LASTEXITCODE). Fix the reported cause and rerun." }
