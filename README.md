# Portable AI setup

Recreate the documented Claude Code + Codex environment on another machine. Provider skills, agents, plugins, binaries, and runtimes are downloaded from their original publishers. This repository contains the installer, pinned source manifest, personal rules, adapters, tests, and local custom skills.

Browse the [custom skill catalog](custom/skills/README.md) to share or install an individual skill.

[Hermes Agent](docs/HERMES.md) is included in the normal one-click setup:
`bash install.sh` or `.\install.ps1`. Its shared agent skill is included in `custom`;
its runtime is downloaded directly from pinned NousResearch source. Use
`--only hermes` or `-Only hermes` only for selective installation or repair.

For model selection, use the shared [AI model comparison skill](custom/skills/ai-model-comparison/SKILL.md) to keep exact-product scores separate from unmatched model references. See the [agentic model comparison](docs/AGENTIC_AI_MODELS.md) and [decision AI comparison](docs/DECISION_AI_MODELS.md): quality evidence, pricing, CPU/GPU sizing, and SemIf/Laya options from 4 GB systems to large GPU deployments.

## Install

On **Ubuntu 24.04+, Debian 12+, or macOS with Homebrew**, run as the user who will use the tools:

```bash
git clone https://github.com/hiakki/ai_setup.git
cd ai_setup
bash install.sh
```

The single-command entry point is:

```bash
curl -fsSL https://raw.githubusercontent.com/hiakki/ai_setup/main/bootstrap.sh | bash
```

Allow at least **12 GiB free disk space** for packages, builds, caches and browsers. Linux asks for sudo only for OS packages. The AI environment is installed for the invoking user, not globally for every server account. macOS needs Homebrew and its command-line tools first. Start a new shell/client after installation so PATH, skills, roles, and hooks reload.

On **native Windows x64 (Windows 10/11 or Server 2022+)**, run `install.ps1` from the checkout in PowerShell 5.1 or 7. **No Ubuntu or WSL is required.** Tools, skills, roles and configuration install into your Windows user profile:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Allow **20 GiB free disk space** for a fresh Windows setup. The launcher installs Python 3.12 and Git for Windows if needed, then native Node, clients, graph tools, FFmpeg and browsers. Git Bash supplies the shell needed by some provider scripts. Graft's native parser requires Microsoft C++ Build Tools; if missing, the installer downloads Microsoft's signed installer and Windows asks for elevation. If Windows requests a reboot, reboot and rerun the same command. Windows ARM64 is not currently supported by this launcher.

After pushing this native-Windows change, the download-and-run command is:

```powershell
& ([scriptblock]::Create((Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/hiakki/ai_setup/main/install.ps1').Content))
```

Start a fresh terminal after installation to load the user PATH. Existing WSL installations remain separate; run `install.sh` inside a chosen WSL distribution if that is your intended environment. Actual Windows execution is pending. The included GitHub workflow exercises Windows PowerShell 5.1 and PowerShell 7 after you push.

## What gets installed

| Component | Contents / source |
| --- | --- |
| Clients and runtimes | Pinned Codex, Claude Code, Node, Bun, Skills CLI, Graft, Playwright MCP; OS FFmpeg |
| Shared provider skills | Emil, Taste, Impeccable, Addy Osmani engineering, Anthropic incident response, marketing, ECC video editing, ScrapeCreators, Superpowers, TypeSafe, Vercel discovery, OpenAI utilities, PowerShell Windows CLI |
| Specialist roles | 32 selected roles fetched from `msitarzewski/agency-agents`; two VoltAgent PowerShell roles; three Codebase Memory roles; five blog roles |
| Blog | All 32 upstream skills, both clients' role adapters, isolated Python runtime and Chromium rendering |
| gstack | Pinned official suite, built tools, prefixed Claude/Codex skills, shared source checkout; no optional learning or automatic upgrades |
| Graph integration | Codebase Memory and Graft, provider-generated hooks and guidance, registered once per client |
| Design/browser | Isolated headless Playwright MCP; Figma remote MCP and official Codex Figma plugin |
| Rules | Portable global preferences, workflow/release evidence rules, project-onboarding reference, local AI Git exclusions |
| Custom additions | Laya, SRE incident investigation, HyperDX regression memory, build-usable-apps, social-rights-review, india-card-research, auditable-business-workflows, reliable-web-app-operations, Hermes agent guidance, ai-model-comparison |
| Hermes | Included by default: pinned NousResearch runtime, shared-skill discovery and Claude/Codex guidance; provider login is separate |
| Context7 | Default remote documentation MCP for both clients; anonymous access, existing authentication preserved |
| UI skills | Default `create-design-md` and `fixing-metadata`, from pinned `ibelick/ui-skills` |
| Strix (optional) | Native checksum-verified CLI and nine upstream security skills; no automatic scans or Docker installation |
| SkillUI (optional) | Pinned global `skillui` CLI for project design context; local directory mode needs no browser or API key |

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

Reusable project skills are now shared globally: [scope, sources and migration](docs/GLOBAL_SKILLS.md). The skills component also downloads Anthropic testing strategy, Vercel web design guidelines and Wshobson quantitative research skills from pinned original providers. Project decisions, conversation records and application-specific agents remain with their projects.

The installer preserves unrelated configuration. It refuses conflicting existing skill folders, edited managed files, mismatched source revisions, duplicate role names, and conflicting MCP definitions. It backs up files before merging configuration. It does not automatically delete or replace an older setup that it cannot prove it owns.

On Windows, an existing local Playwright MCP entry is reused with its configured browser. For example, `npx -y @playwright/mcp@latest --browser chrome` keeps using Chrome and skips the installer's Chromium download. Each client's existing Playwright entry is preserved; a client without one receives the existing launch settings. With no existing local entry, the installer sets up its managed Chromium browser. The full installation smoke check still tests the configured browser.

Rerun the same command after a failed download; installed component state is retained. Review a reported collision before relocating that specific old file. Do not delete your entire client configuration. Backups are under `~/.local/state/ai-setup/backups/`.

Browser downloads use a five-minute socket timeout instead of Playwright's 30-second default. This applies to Playwright MCP, blog/Patchright and gstack through their shared installer environment. An explicit `PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT` value is preserved. To recover an older checkout from a browser download timeout, rerun from PowerShell with:

```powershell
$env:PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT = '300000'
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Keep the original `-HomeDirectory` argument if you used one. Completed browser downloads are reused; an incomplete archive may need to download again. This timeout controls inactivity during download, not the maximum total download duration. See [Playwright's download configuration](https://playwright.dev/docs/browsers#install-behind-a-firewall-or-a-proxy).

If the native Windows Playwright MCP download still reports a timeout after this increase, rerun `./install.ps1` from the updated checkout. The pinned downloader can hit Node's five-second connection timeout before IPv6-to-IPv4 fallback completes, while its error prints the much longer configured timeout. The Windows integration step now preloads `config/playwright-download-timeout.cjs` for the download command and its workers so that the configured timeout also applies during connection establishment. This leaves TLS verification, proxy settings, address selection, and browser extraction with the provider and does not persist Node options.

## Preview, verify, and selective recovery

```bash
bash install.sh plan                      # No writes/downloads; Python 3.11+ needed
bash install.sh verify                    # Installed paths, rules and config
bash install.sh install --only skills,agents,custom,rules
~/.local/share/ai-setup/venv/bin/python smoke.py  # Actual local graph/browser flows
```

Default components: `runtime,skills,agents,custom,blog,gstack,integrations,context7,rules,figma,hermes`.
Both entry points select `all` by default, using the shared default profile in
`setup.py`. Optional components are `strix,skillui`; `all` does not install them.
Use `--only all,strix,skillui` or `-Only 'all,strix,skillui'` for the default profile plus both tools.
Hermes provisions its own upstream runtime.
Install `runtime` before the other runtime-dependent components. `--home /absolute/path`
selects a separate installation home; it is useful for testing, not a way to install
into another user's account with the wrong ownership. Hermes on Windows requires
the current user's home because its upstream installer registers that user's PATH.

Windows equivalents, from the checkout:

```powershell
.\install.ps1 -Action plan
.\install.ps1 -Action verify
.\install.ps1 -Only 'skills,agents,custom,rules'
# Isolated installation (does not persist that home's PATH in your user profile):
.\install.ps1 -HomeDirectory 'C:\AI setup test' -Only 'skills,agents,custom,rules'
& "$HOME/.local/share/ai-setup/venv/Scripts/python.exe" smoke.py
```

`plan` needs an existing Python 3.12–3.13 on Windows and makes no downloads. Directory junctions share Windows skill folders without requiring Developer Mode. Native MCP registrations use executables directly; terminal commands have Windows and Git Bash launchers.

To add the new tools to an existing installation:

```bash
bash install.sh install --only context7,skills,strix,skillui
```

```powershell
.\install.ps1 -Only 'context7,skills,strix,skillui'
```

`skills` installs the provider skill selection, including the two new UI skills.
SkillUI needs Node 18+ and npm (already supplied by `runtime`). Strix installs a native
CLI on Windows; local scans additionally need a Docker Linux-container backend.
See [web development tools](docs/WEB_DEVELOPMENT_TOOLS.md) for agent discovery,
usage, authentication, preservation behavior and runtime limits.

The installer pins top-level npm versions and Git commits. OS packages and upstream Python dependency ranges remain platform/resolver dependent; this is not a byte-identical OS image. Review and change pins deliberately. Do not run a generic `skills update` over the separately managed blog/gstack adapters. Replacing an existing source revision is intentionally not an automatic destructive operation.

Graft uses a separate Node 20 runtime because its pinned native parser failed to build with Node 24 on Linux ARM. Other tools use Node 24. The installer trusts only the exact provider hooks it installs, using hashes reported by Codex itself. It does not enable optional gstack learning, desktop-browser integration or automatic upgrades.

Playwright's Chromium sandbox is enabled by default. Run under an unprivileged account with browser sandbox support. In an isolated container that cannot support it, explicitly use `AI_SETUP_BROWSER_NO_SANDBOX=1 bash install.sh`; this disables that browser sandbox and relies on the container's isolation. Keep the same option when rerunning the installer in that container.

## Account and private service setup

Installation does not transfer authentication, authorize spending, or copy secrets. Log into Codex (`codex login`) and Claude (`claude`) on the new machine. Figma authorization is separate for each client (`codex mcp login figma`; Claude `/mcp`).

Client model choices and permission policies remain account-specific. The observed local choices were Codex `gpt-6-astra` with medium reasoning and Claude `opus[1m]`; choose available models after login. Existing choices are preserved.

For Laya, provide `LAYA_ENDPOINT` and `LAYA_API_TOKEN` through your private environment, or provision `~/.config/laya/config.json` containing `endpoint` and `token`. Use mode `0600` on Unix; on Windows the file must belong to your current user and grant access only to that user, SYSTEM and Administrators. Then run the bundled synthetic check:

```bash
python3 ~/.agents/skills/laya-decisions/scripts/predict.py \
  --input ~/.agents/skills/laya-decisions/assets/smoke-request.json
```

In PowerShell, use the installed interpreter:

```powershell
& "$HOME/.local/share/ai-setup/venv/Scripts/python.exe" "$HOME/.agents/skills/laya-decisions/scripts/predict.py" --input "$HOME/.agents/skills/laya-decisions/assets/smoke-request.json"
```

TypeSafe and ScrapeCreators need their own credentials before live use. Private HyperDX, Servinoza and Stripe integrations are account/project-specific; they are not silently pointed at the original workstation's services. See [connections](docs/CONNECTIONS.md). No model weights, benchmark environments, paid services, production endpoints or authentication caches are replicated.

## Development checks

```bash
python3 -m venv .work/venv
.work/venv/bin/pip install -r requirements.txt
.work/venv/bin/python -m unittest discover -s tests -v
python3 custom/skills/laya-decisions/scripts/test_predict.py
bash -n bootstrap.sh install.sh
# Optional, with PowerShell installed: simulated native bootstrap/process boundaries
python3 tests/check_windows_launcher.py --pwsh /absolute/path/to/pwsh
```

Actual platform results and remaining limits are recorded in [verification](docs/VERIFICATION.md). Installation, local runtime checks, account authorization, and paid/provider-backed workflows are separate evidence levels.
