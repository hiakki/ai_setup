# Agent Reach across projects and machines

Agent Reach is installed once per OS user for Claude Code and Codex. Use it for
social-platform research, available video subtitles, RSS and public-page extraction
when those adapters add value. Ordinary browser search, Context7 documentation,
Figma design and local code graphs keep their existing roles. Installation makes
the capability discoverable; it does not guarantee agent invocation or better
answers without checking the actual retrieved evidence.

## Providers and installation

- [Agent Reach](https://github.com/Panniantong/Agent-Reach): 1.5.0, commit
  `94f06c1969dfc1834001269d79d3ad0972d9dee6`, MIT.
- [OpenCLI](https://github.com/jackwener/opencli): npm `@jackwener/opencli` 2.0.1,
  Apache-2.0; the npm integrity is pinned in `manifest.json`.
- Isolated Python dependencies: yt-dlp 2026.8.19 and feedparser 6.0.14.

The installer fetches original provider sources/packages, preserves their licenses
and keeps them in user storage, not this Git repository. Other dependency versions
resolve at install time; this is not a full transitive dependency lock. OpenCLI's
installed package-lock records that resolution. The managed Node version is shared
with the rest of ai_setup. No browser download, browser launch, MCP registration,
account import, cron, publishing or model inference occurs during installation.

Fresh setups include `agentreach` in both default entry points. Existing machines
need this checkout revision and one explicit installation:

```bash
# macOS / Ubuntu / Debian, from the ai_setup checkout
bash install.sh install --only agentreach
```

```powershell
# Native Windows x64, no WSL
.\install.ps1 -Only agentreach
```

Use the same command to repair/reapply a reviewed version. Local modifications
are preserved by failing with a conflict rather than overwriting them. Runtime
updates are explicit; `ai-setup update` does not upgrade this component. Other
machines do not receive unpublished local changes automatically.

## Discovery and operation

The adapted English provider skill and its original references live in
`~/.agents/skills/agent-reach/`; Claude has a link/junction under
`~/.claude/skills/agent-reach/`. Codex discovers the shared catalog. Both clients
receive a scoped global instruction block. Use the next turn or a new session
if a client has retained an old skill catalog. No project-local setup is needed.
The installed skill includes this guide at `references/ai-setup.md`, independently
of whether an older aggregate documentation bundle has local edits.

Commands are under `~/.local/bin` (native `.cmd` wrappers on Windows):

```text
agent-reach --version
agent-reach doctor --json
agent-reach-yt-dlp --help
agent-reach-python -c "import feedparser; print(feedparser.__version__)"
opencli list
```

`agent-reach-python` runs the isolated Python with feedparser/requests available.
`agent-reach-yt-dlp` uses that same environment without replacing another installed
yt-dlp. The Agent Reach launcher adds its private Python scripts to its child PATH,
so doctor can find its own video dependency. OpenCLI uses the managed Node runtime
and `CI=1` to suppress update checks and adapter synchronization. Its bundled
adapters remain available; npm lifecycle scripts are not executed.

Example project request:

> Use Agent Reach to research public discussions about this product category.
> Use accessible sources, cite them, distinguish opinion from evidence, and tell
> me which requested platforms could not be read. Keep the findings in this app's docs.

For video research, use subtitles only when available. They do not establish what
was visually demonstrated. Facebook's adapter does not establish support for
every Reel link or automatic transcription. Test the actual URL; never label a
metadata-only fetch as watching a video.

## Available versus configured

| Capability | Installed route | Remaining requirement |
| --- | --- | --- |
| Public pages | Upstream Jina Reader instructions; existing browser tools remain preferred | Public network/service access; no private URLs |
| RSS/Atom | Isolated feedparser + requests | Reachable feed |
| Video metadata/subtitles | Isolated yt-dlp | Accessible video and available subtitles; sites may block requests |
| GitHub | Existing gh/browser tools | gh is reused if present; GitHub authentication is personal |
| Facebook, Instagram, Reddit and other OpenCLI adapters | OpenCLI and bundled adapter code | User-approved Browser Bridge and logged-in desktop browser; target read verification |
| Exa/mcporter, dedicated X/Reddit/Bilibili CLIs, LinkedIn, hosted transcription | Not installed by this component | Separate requested setup and any required account/key |

Social access is not configured by copying credentials between machines. A server
without a logged-in browser cannot use desktop-session adapters automatically.
Follow the pinned OpenCLI provider's Browser Bridge guide when that connection is
requested. Do not silently install additional backends or automate login.

Agent Reach's doctor output is an availability hint, not end-to-end proof. Some
checks only confirm a package/command or credential presence. Require relevant,
non-empty output from the actual requested read. Preserve rate limits, failures
and missing-source caveats. The CLI is free software; external services, proxies
and transcription providers can have quotas or costs.

The integration policy in `config/AGENT_REACH.md` overrides the provider's broad
"use for every URL" trigger and setup/update instructions. The installed entrypoint
has a narrower description; original provider files remain in the source checkout.
Credentials, browser profiles and raw private findings never enter ai_setup,
Hindsight or Agent Wiki. Shared learning publication remains reviewed and explicit.

## Verification

Run from this checkout using ai_setup's bootstrap Python:

```bash
~/.local/share/ai-setup/venv/bin/python tests/check_agentreach.py --home "$HOME"
```

```powershell
& "$HOME/.local/share/ai-setup/venv/Scripts/python.exe" tests/check_agentreach.py --home "$HOME"
```

The maintained check exercises real launchers, bundled adapter discovery, RSS
parsing and video metadata extraction from a disposable loopback fixture, plus a
deliberately missing media URL. It does not log into social accounts or infer live
YouTube/Facebook access. The workflow `.github/workflows/agent-reach.yml` covers
macOS, Ubuntu and native Windows; a separate Debian container check is documented
with the actual results below. CI definitions are not evidence that CI has run.

### Observed results — 20 October 2026

- macOS ARM64: current-user installation, real launchers, adapter discovery,
  RSS/video fixture and missing-URL checks passed. Codex's actual `skills/list`
  returned exactly one global Agent Reach skill from each of two project fixture
  directories; the Claude link resolves to that same skill. No model run was used.
- Ubuntu 24.04 ARM64 and Debian 12 ARM64: fresh isolated installs, repeat installs,
  managed-path verification and the same real CLI/fixture checks passed through
  the shared Python dispatcher. These were disposable containers, not tests of
  every package-bootstrap branch in install.sh.
- Public network checks on macOS: Agent Reach's actual Jina adapter returned
  Example Domain; the isolated requests/feedparser fetched 50 entries from the
  Python Insider Atom feed. An initial obsolete Python RSS URL returned 404;
  using the actual blog feed corrected the test source, without hiding the error.
- Native Windows x64: launchers and installer selection have unit coverage and
  a maintained native CI job, but actual Windows execution is **UNVERIFIED** here.
  No WSL dependency was added. x64 macOS/Linux execution was not performed here.
- Full installer regression suite: 158 tests, 154 passed and four existing
  platform skips; seven focused Agent Reach tests passed after final test additions.
  The default-dispatch fixture was updated to mock the new component explicitly.

Two test-harness corrections matter for reuse: PyPI normalizes date-version zeros
while yt-dlp displays them; OpenCLI lists only 25 adapters by default, so absence
from the first page is not evidence that a platform is missing. Checks now compare
normalized versions and query named platforms. The first Ubuntu tmpfs mount was
non-executable; rerunning with an explicitly executable disposable mount passed.

Current-home aggregate setup verification still reports pre-existing changed
`reference/GLOBAL_RULES.md`, the docs bundle and older global instruction blocks.
These were preserved. Agent Reach's focused runtime/skill checks pass independently;
this is not a claim that the entire existing setup is free of drift. On fresh
Linux homes aggregate verification passed for all eight managed paths.

Doctor reported five core channels available on this machine, seven requiring
configuration and four off. These are upstream diagnostics, not live social/video
access tests. Browser Bridge, social login, live video subtitles and visual
understanding remain **NOT TESTED**. Additional backend setup is not implied.

Canonical source: `hiakki/ai_setup`, `docs/AGENT_REACH.md`, `agentreach_runtime.py`,
`config/AGENT_REACH.md`, `manifest.json`, `tests/check_agentreach.py` and
`tests/test_agentreach.py`; unpublished working tree at base
`50cd10a002b7eb7e5479f4f500ca19d7b350b5c2`. Local evidence is ignored under
`.ai-local/one-off/agentreach-*`; the installed report is
`~/.local/state/ai-setup/agent-reach-report.json`. This establishes installation
and bounded reads, not improved model scores, every-site access or remote rollout.
