# One conversation with a specialist team

OpenRig coordinates persistent Claude Code/Codex sessions. ai_setup supplies a
central roster of 14 roles, a lead conversation and project-specific team state.
It complements the central skills, Hindsight and Agent Wiki; it does not replace
their ownership/review process or automatically publish conversations.

## Installation and platform coverage

`bash install.sh install --only openrig` installs the pinned runtime, tmux when
missing, the shared `openrig-team` skill and `ai-team`. On Ubuntu/Debian it also
installs missing Python, native build tools and `procps` through apt. Full new installations
include this component. Existing projects need no per-project tool installation.

| Platform | Execution mode |
| --- | --- |
| macOS, Ubuntu/Debian | Local OpenRig with Node 22 and tmux |
| Native Windows | Native `ai-team.cmd` SSH entrypoint; execute on an authorised macOS/Linux host |

Windows: `.\install.ps1 -Only openrig`. This does not install Ubuntu/WSL or claim
native Windows OpenRig execution. Configure a normal personal SSH host alias and
install ai_setup on that host first. No host, credentials or private checkout is
invented by the installer. Remote SSH requires the OS OpenSSH client.

OpenRig 0.6.13 is downloaded from its original npm provider and checked against
the manifest integrity; upstream revision is recorded in `manifest.json`.
Node 22 is isolated from the other ai_setup runtimes for Apple Silicon compatibility.
SQLite's native install step is run explicitly. Other npm lifecycle hooks and the
upstream `rig setup` wizard are skipped. Dependency resolution is recorded in the
installed npm lockfile; transitive dependencies are not a repository-wide lock.

## Use in an existing or new project

The project directory must exist. A new application can begin as an empty directory;
an existing application retains its existing checkout, instructions and docs.

```sh
ai-team roles
ai-team prepare --project /absolute/path/to/project
ai-team start --project /absolute/path/to/project
ai-team chat --project /absolute/path/to/project
```

Codex is the default runtime and uses the operator's configured model/login.
Choose `--runtime claude-code` on prepare/start for Claude; that choice is saved
for this project. No second provider subscription is required. Existing team runtime
changes are refused rather than resetting conversations.

The lead is the user-facing conversation. Give it the project requirement there,
or from an existing agent/terminal:

```sh
ai-team send --project /absolute/path/to/project "Review this requirement with backend and QA; return a plan before implementation."
ai-team activate --project /absolute/path/to/project --roles backend,qa
ai-team status --project /absolute/path/to/project
ai-team stop --project /absolute/path/to/project
```

`prepare` writes only private runtime definitions. `start` launches the lead;
`activate` adds a selected specialist pod and starts it. Other roles stay available
in the central roster without running sessions. One atomic startup message supplies
scope boundaries and exact paths to the upstream role and selected global skills,
without copying provider skills into this repository or app-owned skill libraries.
The role roster is in `config/openrig-roles.json` and covers product, architecture,
backend, database, frontend, design, native, QA, security, DevOps, SRE, marketing
and independent review. Marketing uses the existing content/video specialist plus
social and analytics skills; it is not an autonomous publishing account.

The lead records owned work using `env OPENRIG_HOST_SELECTED=local rig queue`;
specialists use `env OPENRIG_HOST_SELECTED=local rig send` for questions and replies.
Pin local routing even inside agents; a pre-existing daemon may otherwise retain
another selected host. The workflow requires actual
acceptance evidence. Role labels, instructions and agreement are not proof of
correctness or an OS sandbox. Keep three specialists active by default; more
requires a task/resource reason. Preserve user approval boundaries for app changes,
external actions and releases. A queued message is not proof it was acted on.

## Remote access from Windows, macOS or Linux

```powershell
ai-team --host my-dev-host roles
ai-team --host my-dev-host start --project /srv/projects/my-app
ai-team --host my-dev-host chat --project /srv/projects/my-app
```

The path is on the remote host. SSH host keys and credentials use the normal SSH
configuration; the launcher does not disable verification. Remote execution does
not sync local uncommitted files. Use the owning repository's normal Git process.
Keep the daemon on loopback. SSH terminal access does not require publishing its
HTTP endpoint. Multi-user account isolation is not supplied by this integration.

## State, side effects and recovery

Definitions live in `~/.local/state/ai-setup/openrig/teams/`; each resolved project
path has its own stable name. The canonical role/skill sources remain ai_setup and
their providers. OpenRig's daemon database stays in its normal `~/.openrig` home.
Do not move or delete these to refresh a skill or reset a conversation.

The installer starts no daemon or agents, adds no MCP registration, changes no
client trust/permission config and installs no additional terminal app. `start`
starts a daemon if needed, with the broad-access kernel and transcript polling
disabled. It does not restart an existing daemon; pre-existing daemon settings
still apply and must be inspected. Native client session history still exists.
Codex activity hooks are disabled for a newly started daemon. Upstream launch
still creates workspace trust and managed project guidance (`AGENTS.md` for Codex,
`CLAUDE.local.md` for Claude), plus runtime metadata. Preserve existing instructions
and inspect `git status`; do not commit personal generated files. Before the first
launch, `ai-team` merges the exact central `ai-local.gitignore` exclusions while
preserving existing entries. It reports tracked instruction/config files without
untracking them. Linked ignore files require an explicit manual merge.

No cron, launch-at-login, automatic publication or live application deployment is
enabled. After `stop`, launching an existing seat uses OpenRig's restoration flow;
never re-import a running team or create duplicate names to work around failure.
If a client waits at login/trust/approval, inspect its terminal and resolve that
specific prompt. Do not use bypass flags or claim readiness from a running tmux
session. `rig doctor`, `rig ps --nodes` and the actual lead response supply different
levels of evidence. Do not upgrade OpenRig outside the pinned component.
Incomplete or incompatible older definitions fail before launch. Preserve their
directory and snapshots and repair against the current format before retrying;
never delete conversations to fix a missing template. There is no automatic
migration of foreign or experimental team layouts in this first integration.

## Verification

Reviewed 20 October 2026 against OpenRig 0.6.13. Source is an unpublished working
tree based on ai_setup commit `50cd10a002b7eb7e5479f4f500ca19d7b350b5c2`.

| Scope | Actual evidence | Status / limit |
| --- | --- | --- |
| Installer and routing tests | Full suite: 171 tests, 4 skipped; final focused OpenRig suite: 11 tests passed | PASS for executed tests; skips are not passes |
| macOS ARM64 runtime | Provider integrity/version, native SQLite, repeated component install, 14-role preflight | PASS |
| macOS Codex coordination | Lead and QA read shared guidance, exchanged a bounded arithmetic check and produced one consolidated reply; backend activation also exercised | PASS for coordination, not a software-quality benchmark |
| Conversation restoration | Stop/snapshot, restore only lead, recover previous QA result and evidence limits | PASS |
| Claude Code | Seat launch reached the provider; actual inference returned HTTP 401, invalid OAuth access token | BLOCKED on user re-authentication; `claude auth status` alone incorrectly appeared sufficient |
| Ubuntu 24.04 and Debian 12 ARM64 | Fresh install, repeated install, native SQLite, runtime version and daemon start/healthy/stop in containers; Debian starts without build tools, tmux or procps | PASS for installation/runtime; Linux agent inference and x64 NOT RUN |
| Native Windows / cross-machine SSH | Native launcher and quoting branch tests; CI matrix prepared | Actual Windows and remote SSH execution NOT RUN |

Independent code review covered routing, startup instruction ordering and old
team definitions. Regression checks pin the local host, deliver boundaries and
source paths in one startup message, preserve missing/incompatible definitions,
and reconcile OpenRig's five-second expansion timeout by inspecting the seat
without resending the mutation. Initial launch uses `rig up`; existing seats use
`rig launch` so restoring a conversation does not rematerialize its team.

Minimal Debian exposed two prerequisites hidden by an existing development image:
SQLite compilation requires `make`/a C++ compiler, and OpenRig's process-liveness
check requires `ps`. The installer now checks these commands and installs only
the missing packages; the regression covers both compilation and process tooling.

The macOS component verification passes independently. The existing whole-home
verification also reports unrelated edited rules/reference-doc bundles; those
edits were preserved rather than overwritten. Test teams were stopped and
archived with snapshots, and their daemon was stopped. No ongoing work was queued.

Installation alone does not prove specialist reasoning quality, Figma access,
cross-machine authentication or a successful application release. Claude requires
successful re-authentication and a new live test. Other machines require publishing
this repository and running their normal installer; availability is not rollout.

Sources: [OpenRig](https://github.com/mvschwarz/openrig),
[AgentSpec](https://openrig.dev/specs/agentspec),
[coordination](https://openrig.dev/tour/parallel),
[cross-machine limits](https://openrig.dev/guides/multiple-machines).
