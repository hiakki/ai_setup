#!/usr/bin/env bash
set -euo pipefail

setup_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
setup_home="$HOME"
setup_action=install
setup_previous=
for setup_arg in "$@"; do
  if [[ "$setup_previous" == --home ]]; then setup_home="$setup_arg"; fi
  case "$setup_arg" in
    plan|verify|install) setup_action="$setup_arg" ;;
    --home=*) setup_home="${setup_arg#--home=}" ;;
  esac
  setup_previous="$setup_arg"
done

if [[ "$setup_action" == plan ]]; then
  exec python3 "$setup_root/setup.py" "$@"
fi

setup_python=python3
if [[ "$setup_action" == install ]]; then
  if [[ ! -f "$setup_home/.local/state/ai-setup/state.json" ]]; then
    setup_disk_path="$setup_home"
    [[ -d "$setup_disk_path" ]] || setup_disk_path="$(dirname "$setup_disk_path")"
    setup_free_kb="$(df -Pk "$setup_disk_path" | awk 'NR==2 {print $4}')"
    if [[ "$setup_free_kb" -lt 12582912 ]]; then
      echo 'A fresh full setup needs at least 12 GiB free for packages, builds, and browser runtimes. Free space and rerun.' >&2
      exit 1
    fi
  fi
  if [[ "$(uname -s)" == Linux ]]; then
    if ! command -v apt-get >/dev/null; then
      echo 'Automatic Linux prerequisites support Ubuntu/Debian. See README for other systems.' >&2
      exit 1
    fi
    setup_sudo=()
    if [[ "$EUID" != 0 ]]; then setup_sudo=(sudo); fi
    # System libraries required by the actual browser and blog-rendering runtimes.
    "${setup_sudo[@]}" apt-get update
    "${setup_sudo[@]}" apt-get install -y --no-install-recommends git curl ca-certificates python3 python3-venv \
      build-essential unzip xz-utils ffmpeg fonts-liberation fonts-noto-color-emoji \
      libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
      libxfixes3 libxrandr2 libgbm1 libcups2 libpango-1.0-0 libcairo2
    # Ubuntu 24.04+ renamed libasound2; ask apt for the provider available on this OS.
    if apt-cache show libasound2t64 >/dev/null 2>&1; then
      "${setup_sudo[@]}" apt-get install -y libasound2t64
    else
      "${setup_sudo[@]}" apt-get install -y libasound2
    fi
  elif [[ "$(uname -s)" == Darwin ]]; then
    if ! command -v brew >/dev/null; then
      echo 'Install Homebrew from https://brew.sh, then rerun this command.' >&2
      exit 1
    fi
    brew install git python@3.12 ffmpeg
    setup_python="$(brew --prefix python@3.12)/bin/python3.12"
  else
    echo 'On Windows run install.ps1, which uses WSL2.' >&2
    exit 1
  fi
  "$setup_python" -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required (Debian 12+ / Ubuntu 24.04+)"'
  setup_venv="$setup_home/.local/share/ai-setup/venv"
  if [[ ! -x "$setup_venv/bin/python" ]]; then "$setup_python" -m venv "$setup_venv"; fi
  "$setup_venv/bin/python" -m pip install --disable-pip-version-check -r "$setup_root/requirements.txt"
fi

exec "$setup_home/.local/share/ai-setup/venv/bin/python" "$setup_root/setup.py" "$@"
