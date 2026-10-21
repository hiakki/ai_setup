# Install and synchronize the shared AI setup

ai_setup owns the portable installer, provider pins, shared skills/roles/rules and
reviewed docs. Each machine has its own client login, credentials, workspaces,
runtime caches and conversations. Fetching Git alone does not install tools;
changing this Mac does not change another machine.

## Commands

| Destination | Fresh install from the published checkout | Full refresh from that checkout |
| --- | --- | --- |
| macOS x64/ARM64 with Homebrew | `bash install.sh` | `bash install.sh sync` |
| Ubuntu 24.04+ / Debian 12+, x64/ARM64 | `bash install.sh` | `bash install.sh sync` |
| Native Windows x64, PowerShell 5.1/7 | `.\install.ps1` | `.\install.ps1 -Action sync` |

After installing this revision, the global command works from any project:

```sh
ai-setup sync --dry-run
ai-setup sync --ref APPROVED_COMMIT_SHA
ai-setup status
```

Replace the placeholder with a published commit; omit `--ref` to use central
`main`. `--source` selects another trusted Git repository. Sync executes installer
code from that source. The preview fetches an isolated checkout and prints a plan
and local-edit blockers; it installs no packages and changes no client settings.

For older machines that do not yet recognize `sync`, first update their clean
ai_setup checkout with `git pull --ff-only`, then use the appropriate command in
the table. Preserve and reconcile local changes before pulling. The downloaded
Unix/Windows bootstrap now refreshes its clean cached `main` checkout; it refuses
dirty/divergent checkouts instead of resetting them. The Unix bootstrap and
downloaded Windows entrypoint choose sync for an existing installation.

## What full sync means

- Default selection is all current default components plus optional components
  already installed on that machine. Newly added default tools are included.
  `--only` / `-Only` explicitly selects a smaller scope; it is recorded as partial.
- Original providers supply packages and skills at manifest pins. Provider-pin
  changes use separate source checkouts; personal source edits are preserved.
- Platform entrypoints supply prerequisites, then the shared installer refreshes
  selected components and runs verification. Full default sync also runs the
  existing synthetic smoke journeys. No inference login is fabricated.
- Existing managed settings can change only when they still match recorded
  installer values. Independent model/provider/auth settings remain intact;
  conflicts stop with an actionable error. Personal files are never force reset.
- A failed operation is recorded as incomplete. Component source revisions and
  the last verified sync scope are recorded separately from the library revision.
  A dirty or unversioned checkout is explicitly marked, never described as a
  published revision. Status records are evidence of the past operation, not a
  fresh live health check or proof that GitHub is up to date.
- `ai-setup update` remains the lighter shared-content path with its existing
  snapshots/rollback. Full sync may change OS packages and runtimes, so that
  content rollback is not a full-machine rollback. Fix the reported cause and
  rerun sync; managed-file backups and old provider checkouts remain available.

Optional tools must be selected on a new machine, for example `--only all,strix,skillui`
or `-Only 'all,strix,skillui'`. They do not start scans. Agent Wiki joins a default
install when an individual key is configured; Hindsight joins when
`HINDSIGHT_MCP_URL` is supplied. Use the documented personal secrets file and
client authentication. Never commit another machine's keys, copy administrator
credentials, or assume a CLI installation proves account access.

## Platform boundaries and acceptance

Windows requires no WSL for the native setup. **OpenRig is an explicit exception:**
the native Windows launcher uses SSH to an authorised macOS/Linux execution host;
it does not provide native Windows OpenRig execution. Windows ARM64 is not
implemented. Application repositories and private project state are not copied.

Before declaring another machine ready: verify the fetched revision, selected
components, fresh/repeat behavior, preservation of operator settings, actual CLI
and skill discovery, and relevant MCP/browser journeys. Record authentication
checks separately. A preview, mocked launcher test, Wiki edit or Hindsight pointer
is not a successful machine installation.

## Readiness corrections — 21 October 2026

The previous update path could not deliver new runtime components, and cached
bootstraps could remain stale. The explicit sync path resolves those omissions.
Review also found and corrected first-install Graphify interpreter relocation,
Codebase Memory managed-binary upgrades, Agent Reach dependency-only runtime
identity, managed MCP executable-path updates, Figma provider-pin refresh, and
Gstack's premature whole-home verification. Gstack provider generation now runs
in an isolated home, imports validated/materialized skill links, and leaves actual
client hooks/settings alone. Gstack and Figma retain the installed revision before
fetching an upgrade, so failed generation/registration remains retryable.

## Executed evidence — 21 October 2026

| Target or check | Actual result and boundary |
| --- | --- |
| macOS ARM64 | Isolated Graphify, Gstack and Codebase Memory fresh/repeat checks passed. Gstack rendered and inspected a synthetic browser page. Actual Codex plugin installation refreshed a synthetic Figma-lifecycle fixture across two revisions; this did not test Figma OAuth or designs. |
| Debian 12 ARM64 | Clean `python:3.12-slim-bookworm` container: Graphify, Context Mode, Agent Reach, OpenRig, custom skills, docs and hub fresh setup passed, followed by the global `ai-setup sync` against a local Git fixture. Runtime versions and component verification passed. |
| Ubuntu 24.04 ARM64 | Existing development image, isolated empty user home: Context Mode, Agent Reach, OpenRig, custom skills, docs and hub fresh/repeat passed. Separate global sync from a clean exact Git revision recorded `dirty: false` and a verified partial scope. This image does not prove every OS prerequisite is absent initially. |
| Native Windows | PowerShell parsing, Standard/Legacy argument passing, sync dispatch, failure propagation, cached-checkout refresh and settings-preservation harness. Windows prerequisites were simulated on macOS; actual Windows execution is still pending. |
| Regression coverage | Failure/retry, ownership and local edits, provider-pin changes, configuration merges, staged binary replacement, safe skill links, immutable revision and two-machine shared-content distribution. Independent specialist source review also performed. |

The combined Linux runs are selected-component checks, **not full default-profile
acceptance**. x64 runtimes, Windows 5.1 execution, live SSH teams, private MCP
authentication and inference were not exercised in this readiness pass. Existing
real-home configuration drift was preserved; the real Mac was not fully synced.
Initial Linux fixture attempts omitted required source files; corrected fixtures
passed. Those fixture failures are not hidden as successful installs.

Full fresh/repeat workflows are prepared for macOS, Ubuntu, Debian and native
Windows, but have not run on GitHub. Debian CI disables Chromium sandboxing only
inside its disposable root container. Production defaults retain sandboxing.
Raw local logs are ignored under `.ai-local/one-off/readiness/`; provider payloads
are fetched during execution and not committed. This evidence belongs to the
unpublished working tree based on `50cd10a002b7eb7e5479f4f500ca19d7b350b5c2`.
Publication and verification on another developer's machine remain separate.
