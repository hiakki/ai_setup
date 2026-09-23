# Project instructions template

Fill in the placeholders from the actual project before adopting this document. Store personal context in ignored `.agents/project-context.md` and connect it through the local client instruction files described in [AI_READY_PROJECTS.md](AI_READY_PROJECTS.md). Preserve existing shared instructions; do not overwrite them. Remove fields that do not apply. These are project instructions, not additional machine-wide rules.

Add the [local AI ignore block](ai-local.gitignore) before generating setup. Keep personal instructions, agent-routing files, MCP configuration, graph caches and AI-only notes out of Git. Inspect tracked/staged files separately; do not untrack existing files without authorization.

## Purpose and boundaries

- Project root: `<absolute path>`
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

For a task that benefits from a specialist, identify the role and bounded responsibility. Use the smallest relevant set and follow the user's delegation preferences. Do not create an agent registry unless the project actually needs routing.
