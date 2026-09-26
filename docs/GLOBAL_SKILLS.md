# Shared skills and project context

Migration date: 25 September 2026. Global means available to the current OS user
across projects. It does not mean every skill should run on every request, or
that application workers read coding-agent skill files.

## Locations and ownership

- Shared installed skills: `~/.agents/skills/<name>/SKILL.md`.
- Claude: `~/.claude/skills/<name>` links to that shared folder (junctions on Windows).
- Custom maintained sources: this repository's `custom/skills/`.
- Provider sources and revisions: `manifest.json`; downloads live in the user's
  `~/.agents/skills/.sources/`, never in this repository.
- Project decisions, conversation summaries, evidence and product-specific agent
  profiles remain local. Read them alongside the relevant shared skill.

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

## What stays in each project

- Elvique: product/calculation rules, agent routing and the shared-skill consumer guide.
- Servinoza_in: architecture decisions, UI lessons and release evidence.
- NarrateAI: `narrateai`, `narrateai-trend-ranking`, pipeline agent profiles,
  rights-review findings, provider choices and publishing restrictions.
- card-savvy-india: product/card data and the Indian Cards Specialist profile.
- DelX: strategy-specific instructions, specialist profiles and dated research.
- career-ops: repository-dependent router, modes, plugins and application workflow.

Historical reports can describe the skills as project-local at the time of their
research. That history is preserved; current instructions point to shared skills.
Reusable corrections belong in the custom source here. Product policies and
verified incident/clip/account facts belong in their project records.

## Install on another machine

Elvique's follow-up migration adds `auditable-business-workflows` and
`reliable-web-app-operations` to the custom collection. Its `operational-admin-ux`
guidance is merged into `build-usable-apps`, including all three supporting
references. See the [engineering playbook](REUSABLE_ENGINEERING_PLAYBOOK.md) for
the merge rationale. With the Hermes adapter, the collection now has nine custom skills; the same
installer discovers them without new platform-specific installation code.

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
