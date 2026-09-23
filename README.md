# Portable AI setup

Recreate the documented Claude Code + Codex environment on another machine. Provider skills, agents, plugins, binaries, and runtimes are downloaded from their original publishers. This repository contains the installer, pinned source manifest, personal rules, adapters, tests, and local custom skills.

## Install

On **Ubuntu 24.04+, Debian 12+, or macOS with Homebrew**, run as the user who will use the tools:

```bash
git clone https://github.com/hiakki/ai_setup.git
cd ai_setup
bash install.sh
```

After this repository has been published, the single-command entry point is:

```bash
curl -fsSL https://raw.githubusercontent.com/hiakki/ai_setup/main/bootstrap.sh | bash
```

Allow at least **12 GiB free disk space** for packages, builds, caches and browsers. Linux asks for sudo only for OS packages. The AI environment is installed for the invoking user, not globally for every server account. macOS needs Homebrew and its command-line tools first. Start a new shell/client after installation so PATH, skills, roles, and hooks reload.

On **Windows**, run `install.ps1` in PowerShell. It installs the environment inside your Ubuntu WSL2 distribution. Native Windows Claude/Codex installations are separate and are not modified. If WSL2 is missing, first run `wsl --install -d Ubuntu` in Administrator PowerShell, reboot if requested, and create the Linux user. Then:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
# For an existing Debian WSL distribution:
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Distribution Debian
```

Windows without an initialized WSL distribution cannot complete unattended through a required OS reboot or initial account creation.

After publishing this repository, the Windows download-and-run command is:

```powershell
& ([scriptblock]::Create((Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/hiakki/ai_setup/main/install.ps1').Content))
```

## What gets installed

| Component | Contents / source |
| --- | --- |
| Clients and runtimes | Pinned Codex, Claude Code, Node, Bun, Skills CLI, Graft, Playwright MCP; OS FFmpeg |
| Shared provider skills | Emil, Taste, Impeccable, Addy Osmani engineering, Anthropic incident response, marketing, ECC video editing, ScrapeCreators, Superpowers, TypeSafe, Vercel discovery, OpenAI utility skills |
| Specialist roles | 32 selected roles fetched from `msitarzewski/agency-agents`; three Codebase Memory roles; five blog roles |
| Blog | All 32 upstream skills, both clients' role adapters, isolated Python runtime and Chromium rendering |
| gstack | Pinned official suite, built tools, prefixed Claude/Codex skills, shared source checkout; no optional learning or automatic upgrades |
| Graph integration | Codebase Memory and Graft, provider-generated hooks and guidance, registered once per client |
| Design/browser | Isolated headless Playwright MCP; Figma remote MCP and official Codex Figma plugin |
| Rules | Portable global preferences, workflow/release evidence rules, project-onboarding reference, local AI Git exclusions |
| Custom additions | Laya skill/helper/tests and two local operational instruction folders |

See [manifest.json](manifest.json) for exact provider URLs, revisions, selections and package versions, and [the inventory](docs/INVENTORY.md) for migration decisions. Research-only model benchmarks and the 72-repository recommendation list are not installed.

## Layout and ownership

```text
~/.agents/skills/<name>/           Shared skills, read directly by Codex
~/.claude/skills/<name>            Claude links/adapters
~/.agents/skills/.sources/         Downloaded provider checkouts and suite runtimes
~/.codex/agents/                  Codex TOML roles
~/.claude/agents/                 Claude Markdown roles
~/.local/bin/                    Tool launchers
~/.local/share/ai-setup/          Node/npm/bootstrap runtime and reference docs
~/.local/state/ai-setup/          Installation state, config backups, verification
```

Downloaded payloads live on the destination machine, outside this Git repository. `.work/` is an ignored development/test area and must never be published. Provider licenses remain in their source checkouts and skill assets. The bundled local instructions have distinct provenance: [custom/README.md](custom/README.md).

The installer preserves unrelated configuration. It refuses conflicting existing skill folders, edited managed files, mismatched source revisions, duplicate role names, and conflicting MCP definitions. It backs up files before merging configuration. It does not automatically delete or replace an older setup that it cannot prove it owns.

Rerun the same command after a failed download; installed component state is retained. Review a reported collision before relocating that specific old file. Do not delete your entire client configuration. Backups are under `~/.local/state/ai-setup/backups/`.

## Preview, verify, and selective recovery

```bash
bash install.sh plan                      # No writes/downloads; Python 3.11+ needed
bash install.sh verify                    # Installed paths, rules and config
bash install.sh install --only skills,agents,custom,rules
~/.local/share/ai-setup/venv/bin/python smoke.py  # Actual local graph/browser flows
```

Available components: `runtime,skills,agents,custom,blog,gstack,integrations,rules,figma`. Install `runtime` before runtime-dependent components. The complete default installs all components. `--home /absolute/path` selects a separate installation home; it is useful for testing, not a way to install into another user's account with the wrong ownership.

The installer pins top-level npm versions and Git commits. OS packages and upstream Python dependency ranges remain platform/resolver dependent; this is not a byte-identical OS image. Review and change pins deliberately. Do not run a generic `skills update` over the separately managed blog/gstack adapters. Replacing an existing source revision is intentionally not an automatic destructive operation.

Graft uses a separate Node 20 runtime because its pinned native parser failed to build with Node 24 on Linux ARM. Other tools use Node 24. The installer trusts only the exact provider hooks it installs, using hashes reported by Codex itself. It does not enable optional gstack learning, desktop-browser integration or automatic upgrades.

Playwright's Chromium sandbox is enabled by default. Run under an unprivileged account with browser sandbox support. In an isolated container that cannot support it, explicitly use `AI_SETUP_BROWSER_NO_SANDBOX=1 bash install.sh`; this disables that browser sandbox and relies on the container's isolation. Keep the same option when rerunning the installer in that container.

## Account and private service setup

Installation does not transfer authentication, authorize spending, or copy secrets. Log into Codex (`codex login`) and Claude (`claude`) on the new machine. Figma authorization is separate for each client (`codex mcp login figma`; Claude `/mcp`).

Client model choices and permission policies remain account-specific. The observed local choices were Codex `gpt-6-astra` with medium reasoning and Claude `opus[1m]`; choose available models after login. Existing choices are preserved.

For Laya, provide `LAYA_ENDPOINT` and `LAYA_API_TOKEN` through your private environment, or provision `~/.config/laya/config.json` with mode `0600` containing `endpoint` and `token`. Then run the bundled synthetic check:

```bash
python3 ~/.agents/skills/laya-decisions/scripts/predict.py \
  --input ~/.agents/skills/laya-decisions/assets/smoke-request.json
```

TypeSafe and ScrapeCreators need their own credentials before live use. Private HyperDX, Servinoza and Stripe integrations are account/project-specific; they are not silently pointed at the original workstation's services. See [connections](docs/CONNECTIONS.md). No model weights, benchmark environments, paid services, production endpoints or authentication caches are replicated.

## Development checks

```bash
python3 -m venv .work/venv
.work/venv/bin/pip install -r requirements.txt
.work/venv/bin/python -m unittest discover -s tests -v
python3 custom/skills/laya-decisions/scripts/test_predict.py
bash -n bootstrap.sh install.sh
# Optional, with PowerShell installed: native argument/error handling using simulated WSL
python3 tests/check_windows_launcher.py --pwsh /absolute/path/to/pwsh
```

Actual platform results and remaining limits are recorded in [verification](docs/VERIFICATION.md). Installation, local runtime checks, account authorization, and paid/provider-backed workflows are separate evidence levels.
