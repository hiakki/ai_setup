#!/usr/bin/env bash
set -euo pipefail

setup_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
setup_home="$HOME"
setup_action=install
setup_only=all
setup_previous=
for setup_arg in "$@"; do
  if [[ "$setup_previous" == --home ]]; then setup_home="$setup_arg"; fi
  if [[ "$setup_previous" == --only ]]; then setup_only="$setup_arg"; fi
  case "$setup_arg" in
    plan|verify|install) setup_action="$setup_arg" ;;
    --home=*) setup_home="${setup_arg#--home=}" ;;
    --only=*) setup_only="${setup_arg#--only=}" ;;
  esac
  setup_previous="$setup_arg"
done

if [[ "$setup_action" == plan ]]; then
  exec python3 "$setup_root/setup.py" "$@"
fi

setup_python=python3
if [[ "$setup_action" == install ]]; then
  # `all` installs defaults; add optional tools with --only all,strix,skillui.
  # Validate against setup.py's canonical component list before package changes
  # whenever a compatible Python is already available.
  setup_validated=false
  if command -v python3 >/dev/null && python3 -c 'import tomllib' >/dev/null 2>&1; then
    python3 "$setup_root/setup.py" plan --home "$setup_home" --only "$setup_only" >/dev/null
    setup_validated=true
  fi
  setup_heavy=false
  setup_prerequisites="${setup_only//[[:space:]]/}"
  case ",$setup_prerequisites," in
    *,all,*|*,runtime,*|*,blog,*|*,gstack,*|*,integrations,*|*,hermes,*) setup_heavy=true ;;
  esac
  if [[ "$setup_heavy" == true && ! -f "$setup_home/.local/state/ai-setup/state.json" ]]; then
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
    "${setup_sudo[@]}" apt-get update
    "${setup_sudo[@]}" apt-get install -y --no-install-recommends git curl ca-certificates python3 python3-venv
    if [[ "$setup_heavy" == true ]]; then
      # Browser/blog libraries belong to the full runtime, not Context7 or CLI setup.
      "${setup_sudo[@]}" apt-get install -y --no-install-recommends \
        build-essential unzip xz-utils ffmpeg fonts-liberation fonts-noto-color-emoji \
        libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
        libxfixes3 libxrandr2 libgbm1 libcups2 libpango-1.0-0 libcairo2
      # Ubuntu 24.04+ renamed libasound2; ask apt for the available provider.
      if apt-cache show libasound2t64 >/dev/null 2>&1; then
        "${setup_sudo[@]}" apt-get install -y libasound2t64
      else
        "${setup_sudo[@]}" apt-get install -y libasound2
      fi
    fi
  elif [[ "$(uname -s)" == Darwin ]]; then
    if ! command -v brew >/dev/null; then
      echo 'Install Homebrew from https://brew.sh, then rerun this command.' >&2
      exit 1
    fi
    setup_packages=(git python@3.12)
    if [[ "$setup_heavy" == true ]]; then setup_packages+=(ffmpeg); fi
    brew install "${setup_packages[@]}"
    setup_python="$(brew --prefix python@3.12)/bin/python3.12"
  else
    echo 'On native Windows run install.ps1 in PowerShell.' >&2
    exit 1
  fi
  "$setup_python" -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required (Debian 12+ / Ubuntu 24.04+)"'
  if [[ "$setup_validated" == false ]]; then
    "$setup_python" "$setup_root/setup.py" plan --home "$setup_home" --only "$setup_only" >/dev/null
  fi
  setup_venv="$setup_home/.local/share/ai-setup/venv"
  if [[ ! -x "$setup_venv/bin/python" ]]; then "$setup_python" -m venv "$setup_venv"; fi
  "$setup_venv/bin/python" -m pip install --disable-pip-version-check -r "$setup_root/requirements.txt"
fi

exec "$setup_home/.local/share/ai-setup/venv/bin/python" "$setup_root/setup.py" "$@"
