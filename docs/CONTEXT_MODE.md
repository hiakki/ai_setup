# Context Mode: local output processing for Claude and Codex

Context Mode is included in the default installer. It helps an agent process
large logs/tool output and search authorized documents without placing all their
raw text in the conversation. It needs no separate model, API key or hosted server:
each client starts a local stdio MCP process when needed.

Provider: [mksglu/context-mode](https://github.com/mksglu/context-mode).
`manifest.json` pins npm release **1.0.169** and its SHA-512 integrity. The installer
downloads the package from npm and checksum-verifies the managed Node runtime
from nodejs.org. Provider code is not vendored into this repository. Transitive
npm dependencies are resolved during installation and recorded in the installed
package-lock; the pin is not a claim of identical dependency resolution forever.

## Install and use across projects and machines

Fresh machines get Context Mode and Logo Design with `bash install.sh` or
`.\install.ps1`. Run as each developer's own OS user. Existing installations can
add these capabilities from an updated checkout:

```bash
# macOS / Ubuntu / Debian
bash install.sh install --only skills,custom,contextmode,docs
```

```powershell
# Native Windows x64: PowerShell 5.1 or 7; no WSL
.\install.ps1 -Only 'skills,custom,contextmode,docs'
```

These commands refresh all selected shared skills/docs and preserve local edits
by reporting conflicts. For Context Mode alone use `--only contextmode` or
`-Only contextmode`. Runtime upgrades are explicit installer operations;
`ai-setup update` updates shared content and does not upgrade this runtime.
Other machines need the published revision and their own install/update; local
changes to this checkout are not remote deployment.

The installer merges one `context-mode` registration into user-level
`~/.codex/config.toml` and `~/.claude.json`, plus a small guidance block in each
client's global instructions. Existing unrelated settings are preserved. Changed
Context Mode registrations are rejected for review; an unchanged managed entry
can be upgraded. Windows calls `node.exe` directly, with separate path arguments.

Start Claude Code or Codex **from the intended project directory** and reopen
existing sessions to reload the MCP/skill catalog. The local adapter binds project
identity to the MCP process's working directory, avoiding upstream fallback to
stale `PWD` or another window's most recent transcript. Reopen in the new project
when switching roots. Desktop clients must launch their server with that project
as cwd; global registration cannot infer a project from an arbitrary home cwd.

Use a request such as:

> Use Context Mode to inspect this project's large test log. Report failing
> tests, the exit status and exact relevant evidence; retrieve more when needed.

Use `ctx_execute`/`ctx_execute_file` for bounded processing and `ctx_index` plus
`ctx_search` for repeated retrieval. Check returned evidence against the source.
Keep Codebase Memory first for code structure, Context7 for current library docs,
and ordinary file reads for small edits. Context Mode is not mandatory for every
tool call and does not guarantee a better model answer or a fixed token saving.

## Chosen integration boundaries

- **No provider routing/capture hooks or statusline changes.** The upstream
  universal-routing skill is not installed. Its blanket routing would conflict
  with this setup's graph-first/Context7 rules. Automatic transcript capture and
  compaction recovery are not enabled or promised.
- **No npm lifecycle scripts.** Upstream postinstall can modify Claude plugin
  registration. `--ignore-scripts` avoids that side effect and native SQLite
  compilation. The installer verifies Node's built-in SQLite FTS5 support.
- **Local data:** indexed content and tool metadata are stored under
  `~/.local/state/ai-setup/context-mode`, using provider project-scoped stores.
  Do not index credentials, customer data or unrelated projects. These databases
  are not synced, published or substituted for Hindsight/Agent Wiki.
- **Execution permissions:** the provider's “sandbox” is not OS containment.
  Commands have the user's privileges. Existing path scope, approval controls and
  tool restrictions still apply; never use it to bypass a denied operation.
- **License:** the pinned package is Elastic License 2.0. This setup installs a
  local instance for each developer; it does not offer the provider as a hosted
  third-party service. Read its included license before another deployment model.

Canonical reusable guidance stays in ai_setup; current app docs stay with the
app; reviewed shared learning can go to Hindsight and Agent Wiki. Context Mode
handles local working context, not the cross-machine knowledge library.

## Verification

```bash
python tests/check_design_context.py --home /absolute/path/to/installed/home
```

Use the installer venv's Python (on Windows, its `Scripts/python.exe`). This checks
both client registrations through real MCP initialization, JavaScript execution,
index/search and isolation from a second project. It also runs Logo Design's SVG
audit, variant export and HTML preview generation. `--install` is for an isolated
test home: it downloads only these providers and checks repeat installation.
Reports live in `~/.local/state/ai-setup/design-context-report.json`.

The `design-context.yml` workflow runs the launcher and this test on Ubuntu,
macOS and native Windows. A committed workflow is not evidence of a passing run;
record actual execution results in the frontend guide's verification note.
