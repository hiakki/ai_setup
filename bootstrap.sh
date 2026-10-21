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
  else
    if [[ -n "$(git -C "$setup_repo" status --porcelain)" || "$(git -C "$setup_repo" branch --show-current)" != main ]]; then
      echo "Preserving local checkout changes/branch: $setup_repo. Reconcile them before syncing." >&2
      return 1
    fi
    git -C "$setup_repo" pull --ff-only origin main
  fi
  if [[ -f "$HOME/.local/state/ai-setup/state.json" ]]; then
    case "${1:-}" in
      install|sync|update|plan|verify|-h|--help) ;;
      *) set -- sync "$@" ;;
    esac
  fi
  bash "$setup_repo/install.sh" "$@"
}
main "$@"
