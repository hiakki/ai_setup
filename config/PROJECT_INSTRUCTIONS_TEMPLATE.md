# Project instructions template

Read the project's own docs and search the central library for relevant reusable AI guidance. Keep confirmed application facts in the application's existing docs; this template is guidance, not a reason to duplicate them or move them into ai_setup. Personal client routing can point to project docs and global skills. Follow [AI_READY_PROJECTS.md](AI_READY_PROJECTS.md) and [CENTRAL_LIBRARY.md](CENTRAL_LIBRARY.md). Preserve existing shared instructions and remove fields that do not apply.

Add the [local AI ignore block](ai-local.gitignore) before generating setup. Keep personal instructions, agent-routing files, MCP configuration, graph caches and AI-only notes out of Git. Inspect tracked/staged files separately; do not untrack existing files without authorization.

## Purpose and boundaries

- Project identifier and repository: `<portable identifier; keep machine paths private>`
- Product purpose and intended users: `<short description>`
- Current task and acceptance criteria: `<observable outcome>`
- Authorized edit scope: `<directories/files>`
- Generated, vendor, or protected paths: `<paths and handling rules>`
- Product/design sources of truth: `<documents or approved references>`

Read relevant instructions and source before editing. Preserve unrelated changes. Ask before expanding scope. Follow the user's global AI rules where available.

## Environment and commands

Record exact commands supported by this repository; do not invent commands from this template.

| Action | Command / location |
| --- | --- |
| Runtime and package manager versions | `<version files / lockfile>` |
| Install dependencies | `<command and working directory>` |
| Environment variable names and local services | `<example env file / setup guide; no real secrets>` |
| Start local app | `<command; run only when authorized>` |
| Focused tests | `<command and how to select a test>` |
| Lint / type checks | `<commands or not applicable>` |
| Build | `<command or not applicable>` |
| Browser / simulator / device check | `<command or manual steps>` |
| Test data and logs | `<fixture/reset instructions and log location>` |

## Discovery

Use configured graph tools first when project rules require them. Confirm the project and freshness, inspect source for material claims, and check relevant coverage. Fall back to direct source for unsupported or missed areas. Use text search for literals and non-code files. Record any evidence limitations.

Available tools and their purpose: `<only tools confirmed available in this project>`.

## Completion criteria

- The requested acceptance criteria are met with the smallest necessary change.
- Relevant tests and checks pass, or failures and skipped checks are explicitly reported.
- Changed behavior is exercised locally using `<specific flow and expected outcome>`.
- For UI changes, inspect relevant viewport sizes and states, keyboard use, and browser errors as applicable.
- Existing hot reload may be used. Ask before restarting servers unless explicitly authorized already.
- Review the final diff for unrelated changes and accidental sensitive data.
- Report what changed, checks and results, and any remaining limitations. Do not call unverified behavior complete.

## Optional specialist use

For a task that benefits from a specialist, identify the installed role and bounded responsibility. Use the smallest relevant set and follow the user's delegation preferences. New reusable role definitions belong in the central library, never in a project-local registry.
