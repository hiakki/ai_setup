# Make a repository or directory AI-ready

Updated 2026-09-27. Scope: **central authoring, global Claude Code and Codex tooling, minimal local routing**.

## The request to use in any project

Open Claude or Codex in the intended directory and send:

> Make this directory AI-ready using {{REFERENCE}}/AI_READY_PROJECTS.md. Search the central library first and reuse global Claude/Codex agents and skills, Graft, gstack and Codebase Memory. Add the local-AI ignore rules before creating setup files. Inspect the actual project and preserve its existing instructions. Author new documentation, skills and roles centrally; leave only required local configuration and routing pointers. Build/index this project when it contains supported code, verify discovery, the Git guard and exclusions, and report passed/skipped checks. Do not reinstall global tools, restart services or change application behavior.

This authorizes onboarding the chosen directory. It does not authorize changing other projects or publishing anything. In this setup, “memorybase” refers to the already-installed **Codebase Memory MCP**; do not install a new memory product because of that shorthand.

## What is already global, and what is per project

| Capability | Reuse globally | Project-specific work |
| --- | --- | --- |
| Shared skills | `~/.agents/skills`; Claude discovery links under `~/.claude/skills` | Choose the relevant skill; no project copies or links needed just to discover it |
| Specialist roles | Codex `~/.codex/agents`; Claude `~/.claude/agents` | Record a useful lead/reviewer only when needed; use exact installed role names |
| gstack | Existing global source, runtime and host adapters | Invoke the matching workflow from the project root; no `gstack init` step |
| Graft | CLI, MCP registration and existing global integration | Build this project's structural graph |
| Codebase Memory MCP | Binary, MCP registration and machine-local graph storage | Index the exact project root and verify coverage |
| Product context | Central `docs/projects/<project>/` in an authorized public/private library | Route to the central context; verify actual project facts before using them |

Inspect the global skill and role directories listed above to confirm discovery. On native Windows, `~` denotes the Windows user profile; consult [the Windows command reference](WINDOWS.md) for PowerShell equivalents. For installation repair, use the ai_setup repository's README and `bash install.sh verify` (Unix) or `.\install.ps1 -Action verify` (Windows). Do not rerun global installers as ordinary project onboarding.

## 1. Inspect the intended directory

Confirm the absolute path and, if present, Git root. For a directory inside another repository, identify whether onboarding is for the whole repository or one component before changing its root instructions.

Read existing instructions and inspect the working tree, manifests, lockfiles and CI definitions. Preserve shared/team instructions. Do not invent test commands, framework choices or product requirements.

An empty directory can be prepared for instructions and Git exclusions. Defer graphs until code exists. A notes/media-only directory may never need a code graph. Do not initialize Git or scaffold an application merely to make a directory AI-ready.

## 2. Add Git protection before generating AI files

Merge the exact block from [ai-local.gitignore](ai-local.gitignore) into the project's `.gitignore`, once, preserving existing entries. Keep it even when a machine-wide ignore file also covers these names. The `.gitignore` change itself may be committed; the excluded personal setup remains local.

The block covers Claude/Codex directories, legacy local skill/context directories, personal instruction files, MCP configuration and graph caches. New authored notes, plans and handoffs belong in the authorized central library. Generated logs, screenshots and runtime caches can remain ignored locally; they are not authored documentation. Add exact exclusions for other generated paths actually observed. An ignore entry does not authorize creating a local skill or document.

Do not use broad patterns such as `agents*`, `memory*`, `*.json` or `*.md`: they can hide application code and real documentation. Confirm `graft/` is the generated cache before applying that entry to a repository with a similarly named source directory.

**Already tracked files remain tracked.** Inspect them with `git ls-files`; adding an ignore entry cannot untrack them or remove old commits. Report existing tracked personal AI files and obtain authorization before removing them from the index. Do not remove team-owned instructions, run a blanket `git rm --cached`, force-add excluded files, or rewrite history. [Git ignore behavior](https://git-scm.com/docs/gitignore).

For a directory without Git, the `.gitignore` can be prepared now. Git exclusion checks are pending until it is a repository.

“Local-only” here means excluded from source control. It does not change what a remote AI model or connected service receives.

## 3. Search and route to central project context

Run `ai-setup search "PROJECT TOPIC"`, inspect relevant results, then run `ai-setup library`.
Use [CENTRAL_LIBRARY.md](CENTRAL_LIBRARY.md) for binding, freshness and authoring rules.
Create project context under the authorized central checkout's `docs/projects/<project>/`,
using [PROJECT_INSTRUCTIONS_TEMPLATE.md](PROJECT_INSTRUCTIONS_TEMPLATE.md). Private facts
require a separately bound private library. If it is missing, ask for that destination;
do not write them to the public library or a local substitute.

Keep only minimal routing in ignored `AGENTS.override.md` and/or `CLAUDE.local.md` when
needed: the instruction to search the library, a verified absolute path to the central
project entry, and a reminder to read existing team instructions. Preserve existing
content. Do not copy the central entry into `.agents/project-context.md` or create a
project-level skill/agent registry. Verify in a fresh session that the route is usable.

## 4. Build only this project's graphs

Once the root contains supported source code:

```bash
cd '/absolute/path/to/project'

# Structural graph; no paid deep-model pass.
# Avoid Graft creating a separate .ignore file.
graft build --no-ignore
graft check

# Keep the graph in local storage; do not emit the team-sharing artifact.
codebase-memory-mcp cli index_repository \
  --repo-path "$PWD" --mode full --persistence false
codebase-memory-mcp cli list_projects
```

These flags were checked against the installed CLI help. Select the returned project whose root matches the intended absolute path; do not guess from a similarly named project.

Then check its state:

```bash
PROJECT='exact-name-returned-by-list_projects'
codebase-memory-mcp cli index_status --project "$PROJECT"
```

Use the active MCP session to find one known symbol, read its source, and call `check_index_coverage` for every evidence path. Inspect missed/stale ranges directly. A successful index command alone is not complete discovery verification.

Do not run `graft init` by default: global MCP/hooks already provide the integration. If a concrete integration is missing, inspect that missing piece before adding any local wiring. Do not add another MCP server, hook representation or graph product automatically.

## 5. Use the tools according to the task

| Task | First choice |
| --- | --- |
| Architecture, symbols, callers and impact | Codebase Memory MCP; confirm project/freshness, then check evidence coverage |
| Fast source pack or graph fallback | `graft ask "specific question" --source`, `graft callers <symbol>`, or `graft map` |
| Config values, literals, unsupported files | Direct source reads / `rg` |
| Planning a substantial change | Existing `gstack-plan-eng-review`, when the task benefits from it |
| Reviewing a diff | Existing `gstack-review` |
| Browser QA report | Existing `gstack-qa-only`; use the project's intended browser/session |
| Recurring bug investigation | Existing debugging skill or `gstack-investigate`, choosing one workflow |
| Specialized work | Relevant global skill and, when useful and authorized, an existing specialist role |
| Durable project facts / handoff | Authorized central `docs/projects/<project>/`; private library for private facts; no secrets |

Claude invocation example: `/gstack-review`. Codex example: `$gstack-review`. State the diff, project and scope. Shipping, deployment and service-changing workflows require the corresponding task authorization.

Use one discovery tool per question unless the second resolves a real gap. Codebase Memory is a structural graph, not a guarantee that every chat decision is remembered. gstack's optional gbrain/learning features are separate and are not enabled by this guide.

## 6. Verify readiness

In a fresh Claude/Codex session, verify the project root, one loaded local rule, and the availability of one relevant global skill/role. Verify one real graph query and its coverage if indexing applies. Run an existing lightweight baseline check when available; record pre-existing failures. No app restart is needed just to write instructions.

Run `ai-setup guard status --project /absolute/project/path` and
`ai-setup check-project --project /absolute/project/path`. If local `core.hooksPath`
overrides the guard, report that gap and integrate the checker into the existing hook or
required CI within the authorized scope. Do not claim repository enforcement from global
instructions alone. Existing local documents are not automatically migrated.

For Git:

```bash
git check-ignore -v --no-index -- \
  .claude/settings.json .codex/config.toml .agents/project-context.md \
  AGENTS.override.md CLAUDE.local.md agency-agents.json \
  .mcp.json graft/graph.json .codebase-memory/graph.db.zst .ai-local/handoff.md

# These commands only inspect; check for existing tracked/staged AI setup.
git ls-files -- .claude .codex .agents AGENTS.md AGENTS.override.md \
  CLAUDE.md CLAUDE.local.md 'agency-agents*.json' .mcp.json graft .codebase-memory .ai-local
git diff --cached --name-only
git status --short
```

Check **each** expected path in the ignore output; one matching path does not prove all patterns work. `--no-index` tests patterns even for tracked files, so the separate tracked-file inspection is necessary.

Report: root; context files; ignored paths; any already tracked AI files; available skills/roles; Graft and Codebase Memory checks; baseline test; skipped checks and reasons. A plain directory can be instruction-ready while Git/graphs remain not applicable or pending.
