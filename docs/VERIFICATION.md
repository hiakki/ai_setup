# Verification evidence

Checks were run on 2026-09-23. Installation tests use separate homes and synthetic projects; the original workstation's Claude/Codex configuration and credentials were not changed.

## macOS ARM64 — before native Windows changes

All nine installer components completed in an isolated home. Static verification covered 383 managed paths plus instruction blocks and merged configuration. The native clients exposed 151 skills without duplicate names or loading errors, 40 Claude roles, and six enabled/trusted Codex hooks. The official Figma plugin was installed and enabled.

Actual local flows passed:

- Graft parsed a Python fixture and verified its graph.
- Codebase Memory's real MCP indexed, searched and checked coverage of that fixture.
- Graft's real MCP initialized and exposed tools.
- Playwright MCP opened a local web page, clicked its button and checked the changed text.
- gstack's compiled browser opened the page and returned its accessibility snapshot.
- The blog renderer generated HTML and a PDF through its Chromium runtime.

Homebrew and OS prerequisites already existed on this Mac; a clean macOS operating-system bootstrap was not exercised. The temporary installation was removed after retaining its reports to recover disk space.

## Linux — before native Windows changes

Ubuntu 24.04 ARM64 completed all nine components and the same local graph, browser, PDF, skill, hook and role checks. Rerunning the full installer preserved the completed installation and passed. The root-owned Docker test used the explicit `AI_SETUP_BROWSER_NO_SANDBOX=1` option; ordinary installs retain Playwright sandboxing.

Debian 12 ARM64 also completed all nine components, the local smoke flows, eight Laya offline tests and a final integrity check after fixes and reruns. Its older Python 3.11 exposed an extraction API incompatibility; the installer now uses the system tar for checksum-verified Node archives. This Docker test used the same explicit sandbox option as Ubuntu.

## Offline regression checks

After the native Windows changes, 25 regression tests passed on macOS; one native Windows junction test was skipped. Coverage includes immutable source installation, asset preservation, both role adapters, idempotence, Git exclusions, existing rules/configuration, home boundaries, cross-process locking, native executable selection, browser-cache discovery, archive validation, hook trust, UTF-8 RPC transport and failed-report replacement. Nine Laya tests passed, including environment-only credentials and Windows permission-metadata validation. Actual Windows ACL semantics remain for the native runner. Bash syntax checks passed.

The native Windows launcher passed PowerShell 7.6.6 parsing and twelve simulated bootstrap/process cases, plus a PATH preservation/idempotence/isolation check. These cover standard and legacy argument handling, spaces and ampersands in paths, failure propagation, prerequisite handling and downloaded-script checkout. They run under macOS PowerShell with simulated Windows process boundaries; they do not prove native installation. PowerShell was downloaded temporarily from the [official release](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6) and its archive digest was checked.

A real original-provider installation fetched the pinned PowerShell CLI skill and both VoltAgent roles into an isolated home, verified references/helper assets and Claude/Codex adapters, excluded provider Git metadata from the skill payload, and passed a repeat installation/integrity check.

## Native Windows — execution pending

`install.ps1` now targets native Windows x64, with no WSL requirement. `.github/workflows/native-windows.yml` runs the regression suite, installs all components under Windows PowerShell 5.1, verifies the configuration, and repeats the complete installation under PowerShell 7. Both full installs execute the actual CLI, MCP, browser, PDF, client-discovery and hook smoke checks. Logs and reports are retained as Actions artifacts.

The workflow has not run in this session. The user will commit, push and test it; no Windows machine was available locally. Local simulations do not validate Windows installers, MSVC compilation, junction discovery by clients, native browser startup, ACL enforcement or UAC/reboot behavior. The Actions runner already has some prerequisites, so a pass there still does not prove every clean-machine bootstrap path.

The final provenance pass moved four unchanged instruction bodies from local copies to original-provider downloads. A separate real-provider install checks their source pins, reference-path adapters and content hashes against the original local files. Runtime smoke checks above were performed before this source-routing change; the runtime and hook implementation did not change in that pass.

## Limits

- Native Windows x64 implementation is prepared; full Windows execution is pending. Windows ARM64 is rejected by the launcher.
- Intel/x86-64 installations have not been exercised here.
- Model login/inference, Figma OAuth/design operations, private MCP services, Laya authenticated predictions and optional paid blog integrations were not exercised. They need the destination account's credentials and capabilities.
- Native Windows changes have not been committed or pushed in this session. The published `main` download command uses these changes only after the user pushes them there.
- The earlier full macOS/Linux runtime results predate the shared portability changes; current regression checks passed on macOS, but full Unix runtime installs were not repeated in this Windows task.
- Provider commits and top-level package versions are pinned; OS packages and upstream Python dependency ranges are resolved at installation time.

`bash install.sh verify` or `.\install.ps1 -Action verify` checks installed file/configuration integrity. A complete installation also runs `smoke.py`, which exercises the local flows above and writes `~/.local/state/ai-setup/smoke-report.json`. A passing local report does not prove authenticated external-service access.
