# Custom agent skills

Reusable skills for coding agents, with one independently usable folder per skill.
Each directory name is also the skill's identifier in its `SKILL.md` frontmatter.

## Browse the skills

| Skill | Directory | Purpose | Requirements |
| --- | --- | --- | --- |
| AI Model Comparison | [ai-model-comparison](ai-model-comparison/SKILL.md) | Compare exact models, quantizations and agent configurations without inheriting unmatched scores. | Primary evaluation sources and configuration details; matched workload results for deployment rankings. |
| Auditable Business Workflows | [auditable-business-workflows](auditable-business-workflows/SKILL.md) | Keep rule-heavy calculations, status, corrections and historical documents consistent. | Approved domain rules and representative calculation/persistence evidence. |
| Build Usable Apps | [build-usable-apps](build-usable-apps/SKILL.md) | Design and verify forms, onboarding, dashboards and application workflows. | Project context; a browser for rendered interaction checks. Framework-independent. |
| Hermes Workflows | [hermes-workflows](hermes-workflows/SKILL.md) | Invoke Hermes for persistent tasks and reuse shared skills. | `hermes` runtime component (included in full setup) and separately configured model access. |
| HyperDX UI Regression Memory | [hyperdx-ui-regression-memory](hyperdx-ui-regression-memory/SKILL.md) | Investigate HyperDX interaction regressions and preserve verified findings. | An authorized HyperDX checkout and its project evidence. |
| Indian Card Research | [india-card-research](india-card-research/SKILL.md) | Research Indian card terms, compare practical rewards and audit calculations. | Current official issuer sources, or date-applicable evidence for historical audits. |
| Laya Decisions | [laya-decisions](laya-decisions/SKILL.md) | Classify, score or select among supplied choices through Laya. | Python and a configured Laya endpoint with any required credentials. |
| Reliable Web App Operations | [reliable-web-app-operations](reliable-web-app-operations/SKILL.md) | Design repeatable setup, deployment, environment, telemetry and provider-delivery workflows. | Project runbooks and authorized infrastructure/provider access when executing operations. |
| Social Rights Review | [social-rights-review](social-rights-review/SKILL.md) | Review source rights, originality and monetization eligibility separately. | Official platform sources and evidence about the actual assets/account. |
| SRE Incident Investigation | [sre-incident-investigation](sre-incident-investigation/SKILL.md) | Investigate outages and explain causes using correlated operational evidence. | Authorized access to relevant telemetry or supplied incident evidence. |

## Folder structure

```text
custom/skills/
├── ai-model-comparison/
│   └── SKILL.md
├── auditable-business-workflows/
│   ├── SKILL.md
│   └── references/
├── build-usable-apps/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
├── hermes-workflows/
│   └── SKILL.md
├── hyperdx-ui-regression-memory/
│   └── SKILL.md
├── india-card-research/
│   └── SKILL.md
├── laya-decisions/
│   ├── SKILL.md
│   ├── assets/
│   └── scripts/
├── reliable-web-app-operations/
│   ├── SKILL.md
│   └── references/
├── social-rights-review/
│   ├── SKILL.md
│   └── references/
└── sre-incident-investigation/
    └── SKILL.md
```

## Install and use

From the repository root, install all ten custom skills using the existing setup:

```bash
# macOS / Ubuntu / Debian
bash install.sh install --only custom
```

```powershell
# Native Windows
.\install.ps1 -Only custom
```

See the [setup prerequisites](../../README.md#install). Skills install under
`~/.agents/skills/`, with Claude discovery links under `~/.claude/skills/`.
The installer preserves conflicting existing installations rather than silently
overwriting them. New skills become available on the next turn; restart the client
session if its catalog has not refreshed.

To share or install just one skill manually, copy its **whole folder** into the
skill directory supported by the recipient's client. Preserve the directory
name and include all references, scripts, assets and metadata. Private service
configuration and project evidence are supplied separately by the recipient.

Select a skill by its identifier, for example `$build-usable-apps` in Codex, or ask
the agent to read that folder's `SKILL.md`. Load the skill relevant to the task;
installation alone does not connect remote services or integrate application workers.

## Maintaining this collection

Elvique's former `operational-admin-ux` is included in `build-usable-apps`; its
admin references are loaded only when relevant. See the [engineering playbook](../../docs/REUSABLE_ENGINEERING_PLAYBOOK.md)
for merge decisions and task routing.

Use descriptive lowercase names separated by hyphens. Keep each folder name equal
to the frontmatter `name`; treat it as a stable public identifier. Keep supporting
files inside that folder and use relative links so it can be installed independently.

Only locally maintained additions belong here. Third-party skills are downloaded
from their original providers using [the source manifest](../../manifest.json).
See [provenance](../README.md) and [global/project ownership](../../docs/GLOBAL_SKILLS.md).
