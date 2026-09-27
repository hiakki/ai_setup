# Shared skills and project context

Initial migration: 25 September 2026; latest custom sync: 27 September 2026.
Global means available to the current OS user
across projects. It does not mean every skill should run on every request, or
that application workers read coding-agent skill files.

## Locations and ownership

- Shared installed skills: `~/.agents/skills/<name>/SKILL.md`.
- Claude: `~/.claude/skills/<name>` links to that shared folder (junctions on Windows).
- Custom maintained sources: this repository's `custom/skills/`.
- Provider sources and revisions: `manifest.json`; downloads live in the user's
  `~/.agents/skills/.sources/`, never in this repository.
- Application decisions, summaries, architecture and release evidence stay in
  the application's own repository. Reusable AI learning belongs centrally;
  private shared AI material requires an explicitly authorized private source.
  Generated runtime evidence and personal client configuration remain ignored
  locally. Read project docs alongside the relevant shared guidance.

Codex discovers the shared catalog. New skills become available on the next turn;
if a client retains an old catalog, start a new session or read the entrypoint
explicitly. Selection still depends on the task and the client's capabilities.

## Migrated collection

| Skill | Maintained source | Applies to |
| --- | --- | --- |
| build-usable-apps | `custom/skills/`; originally Servinoza_in | Application workflows, forms, dashboards and rendered interaction checks |
| social-rights-review | `custom/skills/`; originally NarrateAI | Source rights and platform monetization reviews for media projects |
| india-card-research | `custom/skills/`; originally card-savvy-india | Indian card terms, reward calculations and historical audits |
| testing-strategy | `anthropics/knowledge-work-plugins`, `bdf7160f2b33598fb0cb3860027e033cbaec7ce6` | Material test strategy and coverage decisions |
| doc-coauthoring | `anthropics/skills`, `33375500bcea98d610eb30ce10ac4e59b89c390d` | Structured collaborative documentation and reader testing |
| web-design-guidelines | `vercel-labs/agent-skills`, `063bee94c3f4df8453406c830b0a7df0f2860278` | UI, interaction and accessibility review |
| backtesting-frameworks | `wshobson/agents`, `4236bb91f8395b0435f1d8b8baf9e8e4c69a8620` | Trading research and backtest methodology |
| risk-metrics-calculation | Same Wshobson revision | Portfolio risk calculations and reporting |

Anthropic and Wshobson retain the revisions previously recorded by their consuming
projects. Vercel's old lock recorded a content hash rather than a commit; the pin
above was resolved during migration and its skill matches both old project copies.
Provider folders and supporting references were compared before deleting local
copies. Licenses stay in the provider checkouts; Anthropic and Wshobson licenses
are also installed with their individual skills.

Existing Laya and HyperDX skills remain global with narrow triggers. The existing
SRE skill is shared under `.agents/skills`, with a compatibility link from its
former `.codex/skills` location. Laya still needs its configured service. HyperDX
still needs that project's evidence; neither is a default for unrelated tasks.

The locally authored `ai-model-comparison` skill adds shared guidance for comparing
exact checkpoints, quantizations and agent configurations. Its maintained source is
`custom/skills/ai-model-comparison`; unmatched model scores remain references, not
scores or ranks for proposed deployments.

## Project-owned material

The following application-specific material remains with its project. It is not
a backlog for migration into ai_setup. Promote generic AI lessons when useful,
without copying private facts or creating competing shared skill libraries. The
[central authoring policy](../config/CENTRAL_LIBRARY.md) records this ownership split.

- Elvique: product/calculation rules, agent routing and the shared-skill consumer guide.
- Servinoza_in: architecture decisions, UI lessons and release evidence.
- NarrateAI: `narrateai`, `narrateai-trend-ranking`, pipeline agent profiles,
  rights-review findings, provider choices and publishing restrictions.
- card-savvy-india: product/card data and the Indian Cards Specialist profile.
- DelX: strategy-specific instructions, specialist profiles and dated research.
- career-ops: repository-dependent router, modes, plugins and application workflow.

Historical reports can describe the skills as project-local at the time of their
research. That history is preserved; current instructions point to shared skills.
Reusable corrections belong in the custom source here. New authored product
policies and incident/clip/account reports belong in their application's own
repository and approved evidence stores. Raw sensitive evidence
is not shared-library content.

## Install on another machine

Elvique's follow-up migration adds `auditable-business-workflows` and
`reliable-web-app-operations` to the custom collection. Its `operational-admin-ux`
guidance is merged into `build-usable-apps`, including all three supporting
references. See the [engineering playbook](REUSABLE_ENGINEERING_PLAYBOOK.md) for
the merge rationale. With the Hermes adapter and AI model comparison guidance, the collection now has
twelve custom skills; the same installer discovers them without new platform-specific
installation code.

The 27 September sync preserves two additional locally authored skills:
`api-docs-governance` and `service-architecture-and-extraction`. They were already
in the shared installation, with Claude/Codex links, but missing from this repo.
Their complete folders, references and UI metadata now ship in `custom/skills/`.
The same sync includes new database/release references in
`reliable-web-app-operations` and cross-service transaction guidance in
`auditable-business-workflows`. Architecture, contract governance and operational
execution retain separate triggers; see the [routing and merge decisions](REUSABLE_ENGINEERING_PLAYBOOK.md).
The follow-up includes release versioning, isolated hotfixes, immutable artifact
promotion and Compose/Kubernetes deployment guidance. These remain references
inside the operations skill, rather than overlapping new skills. The architecture
skill links to the deployment reference. An independent review corrected the
distinction between single-host Compose and ops-managed multi-host orchestration.

The existing global `doc-coauthoring` entrypoint matches the pinned Anthropic source
byte-for-byte. It is now reproduced by the `skills` component directly from that
provider; no copy is stored under `custom/skills/`.
The overlapping local service-extraction addendum in `testing-strategy` is covered
by the architecture skill's security/QA reference, preserving the provider skill
as an upstream-managed installation.

The 27 September workspace scan found 3,058 `SKILL.md` entrypoints, including
hidden project directories, application runtime bundles, provider checkouts and
historical snapshots. Dependency/build/cache directories and `.work` outputs were
excluded. This is an inventory count, not a count of new reusable skills. Recent
project candidates and the shared installations were compared with the maintained
sources. Project routers, company-specific workflows, runtime bundles and snapshots
remain with their owners. NarrateAI's recent trend-ranking skill still depends on
its source map, scheduler and tests; it stays local. No promoted project entrypoint
was moved during this follow-up, so no consumer path rewrites were needed.

The default [Hermes component](HERMES.md) also configures Hermes to discover the
shared skills and adds invocation guidance to the global Claude/Codex instructions.
Hermes memory stays in its own data directory. New clients must support the shared
skill format or be told to read the relevant entrypoint; installing a skill cannot
automatically add tools to arbitrary agents or application workers.

Run the normal installer for the full environment. To add this collection to an
existing compatible environment, run from this checkout:

```bash
bash install.sh install --only skills,custom
```

Native Windows:

```powershell
.\install.ps1 -Only 'skills,custom'
```

The existing installer fetches providers and installs all custom folders, including
references and metadata. It refuses unmanaged or locally edited conflicts. Do not
delete an existing skill to suppress a conflict: compare it and preserve changes
before an intentional migration. No project or global rule grants deployment,
publishing, trading or other external-action authority merely by loading a skill.

## Verification of the 27 September follow-up

- All twelve custom entrypoints pass the skill validator. The two new skill
  folders and the operations folder have no broken relative Markdown links.
- A fresh isolated home installed all custom folders and the pinned Anthropic
  document skill, repeated the installation, and passed verification both times.
- The actual macOS user installation passes its verifier (62 managed paths and
  instruction blocks). All twelve custom folder fingerprints match this repo;
  Claude links and existing Codex compatibility links resolve correctly. The
  document skill matches the downloaded provider folder.
- Reviewed local edits and installer state were backed up before reconciling
  ownership. No project-specific skill was deleted or replaced.
- Installer tests: 10 passed, one Windows-only read-only-file test skipped on
  macOS. POSIX launcher tests: 6 passed. PowerShell syntax, argument forwarding
  and simulated prerequisite tests passed using local PowerShell.
- Native Windows and Linux installation were not rerun for this content/manifest
  sync. Launchers continue to use the shared installer; account-backed workflows
  and the behavioral quality of every skill are outside these installation checks.
