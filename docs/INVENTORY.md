# Local setup → portable installation

Source reviewed: `r&d/AI-env_setup`, its global inventory/discovery/rules, all development guides and manifests, blog adapter, verifier, skills/agents research, and decision-model research/benchmark reports. The downloaded benchmark dependencies and weights are research artifacts, not part of the target machine profile.

The follow-up read of local skill-lock metadata and role names confirmed 35 CLI-recorded skills; TypeSafe, three OpenAI utility skills, blog/gstack and local additions are separately maintained. The local clients each contain 40 roles: 32 Agency, three Codebase Memory, five blog.

## Provider decisions

| Source | Selection |
| --- | --- |
| `vercel-labs/skills` | CLI and find-skills |
| `emilkowalski/skills` | The recorded 12 skills |
| `leonxlnx/taste-skill` | The recorded 13 skills; use declared names rather than source folder names |
| `pbakaus/impeccable` | Shared-host skill, references and launcher |
| `coreyhaines31/marketingskills` | video, social, analytics |
| `affaan-m/ECC` | video-editing only |
| `ScrapeCreators/social-media-research-skills` | trend-discovery only |
| `obra/superpowers` | debugging, TDD, verification |
| `typesafe-ai/skills` | Official guidance; no Jev inference service |
| `addyosmani/agent-skills` | Frontend, security and DevTools skills; historical pins match the local content and reference assets |
| `anthropics/knowledge-work-plugins` | Engineering incident-response skill and its CONNECTORS reference |
| `openai/skills` | Existing pdf, playwright, security-best-practices; retain legacy source explicitly |
| `AgriciDaniel/claude-blog` | 32 skills, five roles, core/presentation extras; portable path/host adapter |
| `garrytan/gstack` | Recorded suite with native per-host generation |
| `msitarzewski/agency-agents` | Actual 32-role local selection, broader than just web/mobile manifests |
| `VoltAgent/awesome-claude-code-subagents` | PowerShell 5.1 and 7 expert roles added for native Windows development |
| `UncertaintyDeterminesYou4ndMe/powershell-windows-cli-agent-skill` | PowerShell/CMD community skill, references and helper scripts; added for native Windows |
| `DeusData/codebase-memory-mcp` | Release binary/checksums and generated native integration |
| `trailhq/Graft` | Published `@nanonets/graft` package, generated integration |
| `microsoft/playwright-mcp` | Pinned npm package, isolated headless Chromium |
| `openai/plugins` | Official pinned Figma plugin, registered through a small generated local catalog |

Recorded revisions are retained where available. For sources without recorded commit IDs, the manifest pins the provider HEAD resolved during this implementation; those are newly verified pins, not invented historical installation revisions. Exact local source folder hashes remain evidence of the old snapshot, not Git commit IDs.

Four initially unattributed skills were resolved through provider history. Addy Osmani's frontend skill matches commit `91d4d07522de9577caf5d213e5bf1acc38fa3df2`; security and DevTools match `cda4542ade0f3c532494b9a48837eb01d39925f1`. Their bundled reference files match too, after adapting reference paths. Anthropic's incident-response body matches the pinned provider file; its formerly missing CONNECTORS reference is fetched and linked into the skill. These third-party instructions are not vendored here.

## Intentional portability changes

The Windows additions are new provider selections, not part of the original Mac inventory. Their pinned original repositories are fetched at install time. The PowerShell skill supplies quoting, UTF-8, error handling and environment guidance; the VoltAgent roles provide separate Windows PowerShell 5.1 and PowerShell 7 review checklists. These are community sources, not Microsoft-authored instructions. Agency Developer Tooling Engineer, DevOps Automator and Test Automation Engineer roles were also used during implementation and remain in the existing selection.

- Replace Mac-specific paths with the chosen destination home.
- Use native Windows executables, PowerShell bootstrapping, directory junctions and Windows ACL checks; retain Git Bash for upstream shell scripts.
- Activate documented global preferences in both clients; Claude previously had no personal CLAUDE.md.
- Preserve additional workflow/release evidence rules from Codex's personal AGENTS.md.
- Generate provider hooks in an isolated home, importing only Claude/Codex configuration. Do not configure the other clients an upstream auto-detector happens to find.
- Keep one Codex hook representation and reject conflicting user settings.
- Keep shared skills at one discovery depth; preserve gstack's host-specific adapters and runtime links.
- Keep custom skills, but never copy the local Laya config or authentication caches.
- Keep research-only repositories, model weights, application repositories, generated project graphs, and old verification logs out of installation.
- Rebuild graphs per authorized project using the installed onboarding guide; never transfer stale indexes between servers.

The manifest provides original-provider provenance. The installation state records what actually ran. Neither proves authenticated access to every configured external service.
