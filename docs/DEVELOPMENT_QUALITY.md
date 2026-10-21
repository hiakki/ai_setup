# Shared development quality

Reviewed 19 October 2026. The `development-quality` skill routes Claude/Codex to
relevant checks. Availability does not automatically improve applications or
establish a measured model-quality gain. Start with the app's existing tests.

## Install once per machine

New installs include `quality`. Existing machines, after obtaining this reviewed
repository revision, run:

```sh
bash install.sh install --only quality,docs
```

Native Windows x64, without WSL:

```powershell
.\install.ps1 -Only 'quality,docs'
```

The shared installer supports macOS/Linux x64 and ARM64 and native Windows x64.
Ubuntu 24.04+/Debian 12+ use native Python prerequisites. `ai-setup update` updates
shared content, not this new runtime component; install it once explicitly.
Nothing is pushed to remote machines. Reload a client session if its skill
catalog has not refreshed. Existing/new projects need no local skill copies.

## Included capabilities

| Capability | Shared implementation | Activation / limit |
|---|---|---|
| Instruction routing | Compact hub guidance; exact duplicate workflow removal | Preserves personal wording, critical global rules and backups |
| Agent evaluation | Promptfoo 0.124.1, upstream eval/provider skills, six-case CLI pilot | Explicit model-run opt-in and existing Claude/Codex authentication |
| React performance/composition | Two Vercel skills at existing pin `063bee94c3f4df8453406c830b0a7df0f2860278` | Select for relevant tasks; verify app framework version |
| Accessibility/visual checks | Shared Playwright + axe test template | Uses app-owned runner, dependencies and reviewed baselines |
| Structural rules | ast-grep 0.51.0 | Read-only patterns first; reviewed rewrites and rule fixtures |
| API contracts | Schemathesis 4.32.1 in isolated Python environment | Authorized target, operations, disposable data and request budget |
| Browser profiling | Chrome DevTools CLI 1.11.0 | On-demand Chrome; no additional global MCP or browser download |
| Output reduction | RTK **OSS** 1.0.1 | Explicit commands; no rewriting hooks, daemon or proprietary engine |
| Component context | Storybook MCP 10.6.2 activation recipe | App-owned compatible server; no invented global endpoint |

Packages come from original npm/PyPI/GitHub providers. Skills use immutable
commits, including Promptfoo `480893f9c6f6dd84bbc2fa71ec9fbc2174885aaf`.
Provider payloads are not cached in Git. Npm root packages/SQLite bindings have
integrity pins; RTK archives have platform SHA256 pins. Schemathesis has an exact
version. Transitive npm/Python dependencies still resolve at installation: this
is not a complete transitive lock. Npm lifecycle scripts are disabled. Promptfoo
includes the required libsql binding but omits optional SDKs; the pilot invokes
the existing coding CLIs instead. React Doctor and new memory systems are omitted.

## Project use and evaluation

Read `custom/skills/development-quality/SKILL.md` or its global installed copy.
The `evaluations/quality` pilot covers a seeded bug, preserving refactor behavior,
responsive HTML structure, source-grounded recall, irrelevant-work avoidance and
recovery from a missing input. Grades inspect files independently. Raw traces
stay in ignored local storage. Recall fixtures do not benchmark Hindsight/Wiki;
HTML structure checks do not establish visual quality or full accessibility.

Set `AI_SETUP_RUN_AGENT_EVALS=1` only for reviewed runs with an agreed usage
budget. Active CLI model/settings/permissions/global skills apply. A disposable
workspace is not OS isolation. Do not use private fixtures or disable approval
controls. For before/after comparison, provision distinct authorized configs,
freeze other variables, set `AI_SETUP_EVAL_LABEL` and repeat fresh runs. Unknown
token cost stays unknown. A single run is not a stable product score.

`templates/quality` contains app-owned starting points. Adapt them within an
approved application task; keep the shared skill global. Application tests,
schemas, baseline screenshots, design contracts and evidence stay with the app.
No app repository changes, scans, paid runs, Storybook services or browser sessions
are implicitly authorized by installation.

## Evidence and recovery

`tests/test_quality.py` checks platform selection, native launcher rendering,
preserving user edits, exact instruction deduplication and rejecting claimed
success without correct behavior. `tests/check_quality.py` runs real CLIs against
synthetic inputs: AST matching, RTK failure status, Promptfoo positive/negative
oracles, and Schemathesis healthy/failing loopback HTTP fixtures. It makes no model
calls and stops its own temporary HTTP server. The default smoke path includes
these checks; CI covers both installers on Ubuntu, macOS and native Windows.
The full local unit suite passed 152 tests with four existing platform skips
(148 executed passes). The final focused quality suite passed seven tests,
including positive/negative controls for all six pilot graders.
The shipped six-case Promptfoo configuration validates, and its actual provider
refuses execution without the model-run opt-in. This verifies the guard and
configuration, not a successful Claude/Codex benchmark. Local instruction cleanup
reduced Codex's file from 42,289 to 36,258 bytes and Claude's from 34,745 to 33,393
bytes at this checkpoint; no latency/token-cost improvement is inferred.

Observed: macOS ARM64 install/rerun and CLI checks passed. Linux verification is
also complete on Ubuntu 24.04 ARM64 through `install.sh`, including rerun and
the same positive/negative CLI checks. Native Windows, separate Debian execution, app browser tests,
Storybook connections and comparative agent benchmarks are unverified. No service
restart is required for CLI/skill installation.

Three installation failures were fixed: expand existing sparse checkouts when
selecting more skills at the same commit; explicitly pin the platform SQLite
binding omitted by Promptfoo's optional-dependency filter; invoke Schemathesis's
console callable because it has no `__main__` module. Preserve these regressions
when updating pins. Edited managed paths stop installation rather than being
overwritten. Pre-existing global rules/docs drift is separate from this component
and must not be silently marked verified.

The quality component independently installs its guide and maintained examples
under `~/.local/share/ai-setup/quality/`, so they remain available even if a
pre-existing edited aggregate docs bundle blocks `--only docs`. In that case use
`--only quality` for this component and review the unrelated docs differences;
do not reset the recorded fingerprint just to obtain a passing aggregate check.

Sources: [Promptfoo](https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/),
[Vercel](https://github.com/vercel-labs/agent-skills),
[ast-grep](https://ast-grep.github.io/guide/introduction.html),
[Schemathesis](https://schemathesis.readthedocs.io/en/stable/),
[Chrome DevTools](https://github.com/ChromeDevTools/chrome-devtools-mcp),
[RTK](https://github.com/rtk-ai/rtk), [Storybook](https://storybook.js.org/docs/ai).
