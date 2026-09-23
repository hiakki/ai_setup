#!/usr/bin/env bash
set -euo pipefail
main() {
  if ! command -v git >/dev/null; then
    if [[ "$(uname -s)" == Linux ]] && command -v apt-get >/dev/null; then
      if [[ "$EUID" == 0 ]]; then apt-get update && apt-get install -y git ca-certificates;
      else sudo apt-get update && sudo apt-get install -y git ca-certificates; fi
    else
      echo 'Install Git (macOS: Xcode command line tools/Homebrew), then rerun.' >&2
      return 1
    fi
  fi
  local setup_repo="$HOME/.local/share/ai-setup-repo"
  if [[ ! -e "$setup_repo" ]]; then
    git clone https://github.com/hiakki/ai_setup.git "$setup_repo"
  elif [[ "$(git -C "$setup_repo" remote get-url origin)" != https://github.com/hiakki/ai_setup.git ]]; then
    echo "Preserving unrelated directory: $setup_repo" >&2
    return 1
  fi
  bash "$setup_repo/install.sh" "$@"
}
main "$@"
