# Verification evidence

Checks were run on 2026-09-23. Installation tests use separate homes and synthetic projects; the original workstation's Claude/Codex configuration and credentials were not changed.

## macOS ARM64

All nine installer components completed in an isolated home. Static verification covered 383 managed paths plus instruction blocks and merged configuration. The native clients exposed 151 skills without duplicate names or loading errors, 40 Claude roles, and six enabled/trusted Codex hooks. The official Figma plugin was installed and enabled.

Actual local flows passed:

- Graft parsed a Python fixture and verified its graph.
- Codebase Memory's real MCP indexed, searched and checked coverage of that fixture.
- Graft's real MCP initialized and exposed tools.
- Playwright MCP opened a local web page, clicked its button and checked the changed text.
- gstack's compiled browser opened the page and returned its accessibility snapshot.
- The blog renderer generated HTML and a PDF through its Chromium runtime.

Homebrew and OS prerequisites already existed on this Mac; a clean macOS operating-system bootstrap was not exercised. The temporary installation was removed after retaining its reports to recover disk space.

## Linux

Ubuntu 24.04 ARM64 completed all nine components and the same local graph, browser, PDF, skill, hook and role checks. Rerunning the full installer preserved the completed installation and passed. The root-owned Docker test used the explicit `AI_SETUP_BROWSER_NO_SANDBOX=1` option; ordinary installs retain Playwright sandboxing.

Debian 12 ARM64 also completed all nine components, the local smoke flows, eight Laya offline tests and a final integrity check after fixes and reruns. Its older Python 3.11 exposed an extraction API incompatibility; the installer now uses the system tar for checksum-verified Node archives. This Docker test used the same explicit sandbox option as Ubuntu.

## Offline regression checks

Eleven installer regression tests passed. They cover immutable source installation, asset preservation, both role adapters, idempotence, active Git exclusions, existing rule preservation, invalid revisions, unmanaged collisions, changed managed content, home-boundary enforcement, Python helper execution, read-only planning and component validation. Eight Laya tests passed, including the environment-only credential path and validation/error handling. Bash syntax checks passed.

The Windows launcher passed PowerShell 7.6.6 parsing and six simulated WSL cases: success, WSL initialization failure and installer failure, each under standard and legacy native-argument handling. Tests use a home path containing spaces. They caught and verified the fix for legacy PowerShell quote stripping. PowerShell was downloaded temporarily from the [official release](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6) and its archive digest was checked.

The final provenance pass moved four unchanged instruction bodies from local copies to original-provider downloads. A separate real-provider install checks their source pins, reference-path adapters and content hashes against the original local files. Runtime smoke checks above were performed before this source-routing change; the runtime and hook implementation did not change in that pass.

## Limits

- Windows uses WSL2. No Windows/WSL host is available in this environment; its PowerShell launcher has not been executed there.
- Intel/x86-64 installations have not been exercised here.
- Model login/inference, Figma OAuth/design operations, private MCP services, Laya authenticated predictions and optional paid blog integrations were not exercised. They need the destination account's credentials and capabilities.
- The repository has not been pushed. GitHub download-and-run entry points become usable after publication.
- Provider commits and top-level package versions are pinned; OS packages and upstream Python dependency ranges are resolved at installation time.

`bash install.sh verify` checks installed file/configuration integrity. A complete `bash install.sh` also runs `smoke.py`, which exercises the local flows above and writes `~/.local/state/ai-setup/smoke-report.json`. A passing local report does not prove authenticated external-service access.
