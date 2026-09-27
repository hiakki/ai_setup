# Verification evidence

## AI-library scope correction — 2026-09-27

The owner clarified that ai_setup owns reusable AI skills, agents and generic
learning; application architecture, business/design decisions, runbooks and
release evidence remain in the application's own repository. This supersedes
the blanket documentation-blocking policy described in the historical entry below.
Policy references, generated Claude/Codex guidance and the Git guard now follow
that split. No application documentation was moved into this public repository.

The scoped regressions passed: 12 library tests (including real Git commits and
CI range checks), nine shared-update/launcher tests and ten hub tests. Application
docs are allowed while copied skill/agent libraries remain blocked. Fixture-only
hub/launcher tests used `GIT_CONFIG_GLOBAL=/dev/null` to avoid the user's installed
hook intercepting their synthetic provider commits; library tests exercise real
isolated hooks instead. These are local macOS checks, not a Windows execution run.
After applying the update, a disposable repository using the actual installed
user-level hook successfully committed application architecture docs and rejected
a copied skill. Managed installer integrity passed, including the updated global
rules, policy references and installed skill consumers.

An installer help invocation exposed an unintended bootstrap path. Help now exits
through the Python argument parser before package operations. Four argument forms
pass a regression with a package-manager tripwire and no created user installation;
the actual `bash install.sh --help` also returns usage without bootstrap.

The reusable admin-elevation and QA-isolation lessons were added to the existing
UI/workflow skills, validated and applied through the managed custom component.
An independent source review found three stale ownership instructions; those
were corrected. This is local validation and installation evidence, not a claim
that these repository changes have been committed or published.

## Central authoring policy and search — 2026-09-27

- **Installed and exercised on the actual Mac:** the normal
  `bash install.sh update --only docs,hub` installed the search/library/check commands,
  updated both clients' global guidance and the onboarding reference, bound this central
  checkout, and enabled the global Git dispatcher. Installer integrity passed for 71
  managed paths and instruction blocks. `ai-setup search "central authoring"` returned
  canonical and installed entries with an explicit local-freshness label.
- **Actual user-level Git gate:** a disposable repository using the real installed hook
  rejected a staged local documentation commit, forwarded its pre-existing hook, allowed
  a source-code commit, and reported active hook coverage. No consuming project's files,
  hook settings or branch rules were rewritten. No existing documentation was migrated.
- **Regression evidence:** 108 tests ran, 104 passed and four skipped (three native Windows
  checks and the optional dotagents network check previously exercised separately).
  Twelve policy tests cover central/private binding, search boundaries, failed refresh,
  staged-content checking, ignored-file audits, CI commit ranges, hook preservation,
  operator edits, disable/restore, hook stdin/arguments/exit status and local override reporting. Eighteen hub/installer
  tests include custom roles in both client formats and shared recovery/locking.
- **Failures reproduced and fixed:** reference-transaction hooks can run during `git init`
  before repository discovery works; dispatch now uses Git's supplied directory context.
  Nested installer work now retains the inherited lock token, avoiding a false concurrent
  operation failure during central updates.
  A further regression reproduced stdin loss when forwarding through `git hook run`;
  direct execution now preserves input, arguments and status, with a shell fallback for
  shebangless hooks. An actual local Git push through the installed global dispatcher
  passed the original pre-push hook's input/argument checks.
- **Boundaries:** global instructions request search; there is no mandatory tool-call
  interceptor or filesystem sandbox. The Git guard is bypassable and local hooksPath
  overrides are reported. The reusable CI gate is prepared but must be published, adopted
  and made required in each consuming repository. Native Windows/Linux execution of this
  new guard and remote Actions runs remain pending. No private library is bound, and
  private cloning/synchronization is not automated. Publication and scheduled updates
  were not performed.

Policy and usage: [Central library](../config/CENTRAL_LIBRARY.md). Local evidence is
ignored under `.work/library-*.log`. Documentation links/fences, workflow YAML parsing
and Git whitespace checks passed.

Use `python tests/run_tests.py` to isolate fixture repositories from the operator's
global Git configuration. This session excluded an unrelated untracked test draft
(since removed). Running fixtures directly after
enabling the real global guard correctly rejects their local documentation commits;
that is why the reproducible suite runner uses an isolated home.

## Central shared hub — 2026-09-27

The [implementation walkthrough](CENTRAL_AI_HUB.md) describes ownership, installation,
updates, contributions and recovery. Evidence for this change:

- **Actual macOS ARM64 installation:** installed all twelve custom skills using pinned
  dotagents 3.1.0, the shared documentation bundle and the global `ai-setup` command.
  Created the permanent installer Python environment because earlier selective installs
  used the development checkout's interpreter. Retried the normal
  `bash install.sh update --only custom,docs,hub` successfully; integrity verification
  passed for 65 managed paths and instruction blocks. This was an existing-machine
  selective update, not a fresh operating-system bootstrap.
- **Git distribution and recovery:** seventeen hub/installer tests passed. Real local
  Git sources delivered the same revision to two isolated homes; rolling one back left
  the other unchanged. Local edits, independent installer state, source conflicts,
  provenance and concurrent installer activity were checked. Contribution export left
  a reviewable diff without committing or pushing. Bash and locally available PowerShell
  exercised the update adapters; PowerShell simulations are not native Windows evidence.
- **Actual provider:** nine dotagents backend tests passed with the opt-in network test
  enabled. All twelve repository skills were also staged twice with complete byte-level
  checks, including supporting files. dotagents stages custom skills only; original-provider
  skill and agent downloads retain the existing installer pipeline.
- **Full regression pass:** 95 tests ran, 91 passed, and four were skipped: three require
  native Windows and one was the separately exercised opt-in provider network test.
  An unrelated untracked test draft (since removed) was excluded. Independent review identified
  and led to fixes for shared installer locking, bounded snapshots and contribution links.
- **Pending publication and platforms:** these new changes have not been committed or
  pushed. Public GitHub rollout therefore remains pending; fixture Git tests do not prove
  the public branch contains the implementation. The new `shared-hub.yml` matrix covers
  macOS, Ubuntu and native Windows, but has not run remotely. Previous platform results
  elsewhere in this document do not establish that this new hub passed on those platforms.

Local logs are ignored under `.work/hub-*.log`. No scheduled update, paid host, public
documentation site, project rewrite or credential distribution was enabled.

## Web development integrations — 2026-09-26

- **macOS ARM64:** real Context7 anonymous MCP tool discovery, React library resolution,
  and documentation retrieval passed. Pinned UI skills installed from their original
  provider into an isolated home, including Claude links; rerun and integrity checks passed.
  Independent workers ran actual Strix checksum/version/help and nine upstream skill
  installation checks, and actual SkillUI npm installation/local CSS extraction. Both
  optional tools passed repeat installation and managed-state verification.
  The final shared workflow checker also passed on macOS, including the exact installed
  CLI launchers, generated color token, repeat installation and 25-path verification.
- **Debian 12 ARM64:** a fresh disposable `node:24-bookworm-slim` container ran the real
  `install.sh install --only context7,strix,skillui` using a home with spaces. The shared
  `tests/check_web_tools.py` then fetched the two UI skills, repeated installation twice,
  checked Strix, extracted `#123456` into SkillUI's DESIGN.md, and verified all 25 managed
  paths plus configuration/instruction blocks. No browser or Docker sandbox was needed.
- **Regression checks:** 69 tests ran, 66 passed and three native Windows tests were
  skipped on macOS (batch invocation, junctions and read-only file semantics). The unrelated
  untracked test draft (since removed) was excluded. Bash syntax and whitespace checks passed.
  The real PowerShell executable passed 27 launcher checks with simulated Windows
  prerequisites. These simulations are not native Windows execution.
- **Independent review:** fixed stale Context7 state that rejected a later operator
  transport change, with a regression test and reviewer reproduction. Fixed explicit
  UTF-8 decoding in the cross-platform workflow checker after reproducing Windows cp1252
  failure against the actual upstream skill.
- **Pending:** native Windows execution of these new tools and the new
  `.github/workflows/web-tools.yml` matrix. The workflow exercises native Windows,
  Ubuntu and macOS entry points and the same CLI extraction/rerun checks after push.
  Strix scans, model authentication, Docker sandbox execution, cloud uploads and SkillUI
  browser/ultra mode were not run. Installation does not claim those workflows passed.

The Linux image supplies Node/npm; the script installs actual Debian prerequisites and
its Python environment. This is verification of the new selective installation path,
not a repeat of every default component or a fresh macOS operating-system bootstrap.
Local logs are ignored under `.work/web-tools-*.log`. The workflow checker records only
its check summary, not credentials or full client configuration.

The earlier baseline checks below were run on 2026-09-23. Installation tests use separate homes and synthetic projects; the original workstation's Claude/Codex configuration and credentials were not changed.

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

Windows MCP PATH rerun follow-up (2026-09-23): reproduced `configuration.mcp_servers.codebase-memory-mcp.env.PATH` conflicts by installing integrations, reloading saved state, and changing the next terminal's PATH. Windows integration generation now reuses the recorded PATH for Codebase Memory and Graft separately for each client; when no recorded value exists, it preserves an existing configured PATH. Fresh entries still receive the installation environment's PATH. The tests cover changed-shell reruns, distinct Codex/Claude paths, preserved Playwright configuration without browser downloads, and rejection of edits to a previously recorded PATH without changing the configuration file. All 36 regression tests passed. Provider installation and hook-trust calls were mocked in these integration regressions; this does not establish a complete user-profile installation pass.

Windows agent replacement follow-up (2026-09-23): reproduced the reported `WinError 5` rename failure by marking an unchanged managed Claude agent file read-only. `Installer.write` now checks ownership and skips replacement when the expected bytes already match, retaining explicit mode handling and local-edit protection. The regression failed before the fix and passed afterward. The real PowerShell launcher completed `-Only agents` against the isolated installation with `api-platform-engineer.md` read-only and verified 384 managed paths. All 35 regression tests passed. The plan test now explicitly uses an isolated home rather than reading workstation state. The user's file attributes/locks were not inspected, so the precise cause of their access denial remains unconfirmed; this fixes the unnecessary replacement reproduced locally.

Windows existing-`npx` smoke follow-up (2026-09-23): the user's profile run reached successful PDF rendering, Codebase Memory MCP, and Graft MCP checks, then failed to initialize the preserved Playwright command. A local native reproduction showed that Python's list-to-command-line escaping passed backslash-escaped quotes to `cmd.exe`, which rejected `npx.cmd` before Playwright started. The batch fallback now supplies a complete command line with cmd-compatible quoting and delayed expansion disabled. A native regression verifies paths with spaces/ampersands and literal argument metacharacters; all 33 installer tests passed. The exact existing command, `npx -y @playwright/mcp@latest --browser chrome`, initialized and listed tools. A second real `npx` MCP flow used the already downloaded test Chromium and passed navigation, button click, and changed-page assertion. No Chrome download or user configuration change was needed. This verifies the reported startup fix; a complete user-profile installer rerun is still unverified.

Further native Windows checks (2026-09-23): the Codebase Memory binary's `daemon status` diagnostic identified the exact activation blocker: `cache-private - D:\learning: DACL entry 4 grants mutation rights 0x00010112 to untrusted identity (Authenticated Users S-1-5-11)`. This is an ancestor outside the authorized repository boundary; making only the test home private cannot satisfy the provider's ancestor checks. Its permissions were not changed.

Running the seven independent components (`skills,agents,custom,blog,gstack,rules,figma`) completed. Real runtime tests then exposed and fixed the blog renderer's POSIX-only `O_NOFOLLOW`, unprefixed names in copied gstack skills, and Laya's eager home-directory lookup even when an explicit config was supplied. The Windows ACL test fixture now persists only modified security sections without requiring audit privileges. The isolated Codex smoke check explicitly supplies the selected home's skill root and filters discovery results to that home because Windows Codex still scans the real profile's shared skills. After these fixes, 32 installer regressions and nine Laya regressions passed. Actual Graft build/check and MCP initialization, discovery of 151 installed Codex skills without duplicates/errors, Claude role discovery, Figma plugin registration, gstack browsing, blog HTML/PDF rendering, FFmpeg execution, and Playwright MCP navigation/click/assert all passed. Playwright reused the previously downloaded v1243 Chromium. Verification passed for 384 managed paths. Codebase Memory installation, provider hook import/trust, and the complete combined smoke run remain blocked by the ancestor ACL, so this is not a full installation pass.

Full native Windows execution attempt (2026-09-23): ran the complete `install.ps1 -HomeDirectory D:\learning\ai_setup\.work\full-home` under Windows PowerShell 5.1, with temporary files and package caches inside `.work/`. Existing Python, Git and MSVC prerequisites were used. The pinned Node runtimes and npm packages installed; Codex, Claude, Graft, Skills and Bun passed version checks. The full run **failed** during Codebase Memory 0.10.8 installation. Its first attempt rejected inherited `Authenticated Users` mutation permissions on the test home's binary directory. Making only the newly created test home private resolved that error, but the next attempts failed with `activation could not reserve exclusive access; no activation was committed`. An explicit `CBM_RUNTIME_DIR` inside the test home did not resolve it. Later components and the complete smoke suite were not reached. This is failed full-install evidence, not a passing native Windows result. Logs are retained locally in `.work/full-install.log` and `.work/full-install-attempt*.log`; these ignored artifacts are not published. The existing user-profile installation was not used as the test destination.

Windows existing-Playwright follow-up: the integration step now reuses an existing local Playwright MCP command and skips its managed browser download. A regression using `npx -y @playwright/mcp@latest --browser chrome` reproduced the command conflict before the fix. Afterward, all 30 tests passed, including two successive integration runs, configuration verification, preservation of a different Claude Playwright entry, and reuse of the Codex entry when Claude has none. Tests use isolated homes under `.work/`; the user's profile and installed Chrome were not accessed.

Windows browser connection-timeout follow-up (2026-09-23): reproduced the reported Chromium v1243 download failure with `@playwright/mcp@0.0.80` under native Windows and Node 24.14.0. All five attempts failed after roughly five seconds each, even though the diagnostic configured a 15000 ms timeout. Direct HTTP requests worked. The pinned provider applies its request timeout too late to override Node's initial agent timeout; its IPv6-first connection fallback needs longer on this host. Applying the configured timeout to the download process's HTTP/HTTPS agents allowed the real Chromium 153.0.8010.12, headless shell, FFmpeg and Winldd downloads and extraction to complete under `.work/`. The fix is scoped to the native Windows Playwright MCP installation command and its forked workers. A local-server regression reproduces the premature timeout, verifies recovery, and checks worker inheritance while leaving address-family selection and TLS verification unchanged. All 29 regression tests passed; a repeat browser install reused the downloaded files, and the downloaded full Chromium launched headlessly and passed a button-click check. This does not establish a complete user-profile installation.

Browser-download timeout follow-up: the shared installer environment now defaults `PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT` to 300000 ms, preserving explicit overrides. The new child-process regression failed at the old 30000 ms default before the fix; afterward, 27 tests passed with one Windows-only skip. Using the pinned Playwright MCP dependency and this environment, the real provider CLI downloaded and extracted `win64/chrome-win64.zip` on macOS. A repeat install reused that completed browser download. This verifies archive retrieval, not Windows execution or the user's network; their Windows rerun remains pending.

- Native Windows x64 implementation is prepared; full Windows execution is pending. Windows ARM64 is rejected by the launcher.
- Intel/x86-64 installations have not been exercised here.
- Model login/inference, Figma OAuth/design operations, private MCP services, Laya authenticated predictions and optional paid blog integrations were not exercised. They need the destination account's credentials and capabilities.
- Native Windows changes have not been committed or pushed in this session. The published `main` download command uses these changes only after the user pushes them there.
- The earlier full macOS/Linux runtime results predate the shared portability changes; current regression checks passed on macOS, but full Unix runtime installs were not repeated in this Windows task.
- Provider commits and top-level package versions are pinned; OS packages and upstream Python dependency ranges are resolved at installation time.

`bash install.sh verify` or `.\install.ps1 -Action verify` checks installed file/configuration integrity. A complete installation also runs `smoke.py`, which exercises the local flows above and writes `~/.local/state/ai-setup/smoke-report.json`. A passing local report does not prove authenticated external-service access.
