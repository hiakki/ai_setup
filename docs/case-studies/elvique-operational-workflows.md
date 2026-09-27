# Elvique: operational UX, business authority and observability

Reviewed: 28 September 2026. Type: sanitized cross-project engineering case.
Search terms: Elvique, admin UI, onboarding, tables, forms, audit, agents,
architecture, ecommerce, invoices, notifications, observability, Grafana, nginx,
logs, traces, OpenTelemetry, collector, deployment, slowness.

This case preserves reusable decisions from project instructions, the shared-skill
migration record and a dated incident report. It is not the current application
specification or a fresh audit of every implementation. Application rules,
customer data, raw discussions and operational commands stay with their owner.
No application, provider or infrastructure workflow was executed to compile this
case. Read the evidence boundaries before treating a lesson as verified behavior.

## Architecture and workflow decisions

| Area | Source decision or failure | Reuse in another project | Evidence boundary |
| --- | --- | --- | --- |
| Shared business authority | UI, reports, APIs and demo controls must agree on derived values. Status, participation, contribution and earning are distinct policies. | Centralize calculations and approved transitions; keep source facts separate from projections. Resolve conflicting rules before changing financial behavior. | S1 is an architectural requirement, not proof that every consumer complies. No product-specific formulas are exported. |
| Relationship corrections | Referral attribution and hierarchical placement are different relationships. Move, replace, detach and delete have different downstream effects. | Define correction semantics, affected descendants, authorization, retry behavior and audit before implementing controls. | S1 and the existing auditable-workflows skill preserve the design; target invariants need fresh tests. |
| Future ecommerce | Catalog, order, invoice and inventory boundaries must be replaceable without rewriting downstream calculations. | Catalog owns current product data; transactions snapshot relevant facts; historical documents use controlled revisions. Keep related transactional ownership explicit without prematurely splitting services. | S1 records the intended boundary. It does not establish a completed ecommerce implementation. |
| Shared UI defects | The project contract requires consistent forms, bounded selectors and usable trees across screens. | Fix demonstrated shared causes, enumerate affected consumers, and test long values, selected states, open menus, validation, zoom and touch. A component fix alone does not verify every page. | S1 defines the acceptance contract; this review did not rerun all screens or establish its historical cause. |
| Operator continuity | Failed validation and mutations must preserve safe input and search/selection context. | Treat recovery as part of the workflow. Surface actionable errors rather than unexplained scrolling or a full-page reset. | Requirement in S1; use the shared form/table references for implementation checks. |
| Delivery and audit | A provider accepting one channel must not appear as confirmed delivery across channels. | Record per-channel attempts and provider references. The existing shared audit guidance additionally distinguishes original operator identity, changed fields and unknown legacy attribution without exposing sensitive values. | S1 requires channel outcomes and acceptance/delivery distinctions; additional audit practices come from the shared audit reference, not a historical claim about S1. No live provider delivery is claimed here. |
| Agent use | Having an agent registry was not sufficient evidence of review or quality. | Load only relevant roles, assign bounded work, pass current evidence and retain concrete findings. Independent review supplements real workflow tests. | S1 describes project routing; S2 records migration to shared skills. No agent-count or first-pass-quality guarantee. |

Read the maintained skills rather than copying a project's business policies:

- [Build usable apps](../../custom/skills/build-usable-apps/SKILL.md): shared forms,
  tables, selectors, uploads, permissions and rendered verification.
- [Auditable business workflows](../../custom/skills/auditable-business-workflows/SKILL.md):
  source facts, calculations, corrections, historical artifacts and demo isolation.
- [Specialist briefs](../../custom/skills/service-architecture-and-extraction/references/agents-and-acceptance.md):
  bounded ownership, evidence handoffs and independent review.
- [Permissions and audit](../../custom/skills/build-usable-apps/references/permissions-audit-and-destructive-actions.md):
  actor attribution, changed-field descriptions and legacy uncertainty.

## The monitoring incident

The dated report records a dashboard whose service health, datasource and metric
queries succeeded while the signed-in browser could not load a plugin. The
public proxy truncated a large JavaScript asset; the direct origin returned it
completely. A throttled proxy request reproduced the truncation. The worker
identity could not access the proxy temporary directory used by buffering.
The proxy error stream also pointed to a deleted terminal. [S3]

The report records a route-scoped buffering repair, persistent error logging,
configuration validation and a graceful proxy reload without an application
restart. Complete public/origin asset comparisons and actual signed-in dashboard
checks then passed. A protocol error was a symptom, not evidence that the
application, datasource or transport protocol itself needed replacement. [S3]

| Follow-up | Transferable lesson | Recorded limit |
| --- | --- | --- |
| Logs and traces | Validate synthetic ingestion, queryability, the real application emitter and browser correlation separately. | S3 records synthetic production collector evidence and a real local production-build request reaching log/trace stores. Production app instrumentation was not activated. |
| Readiness versus writes | A ready endpoint can coexist with ingestion failure. Inspect write responses, disk/WAL limits and dropped-event counters. | Disposable local collector hit a disk guard; only the disposable test threshold changed. Production safety limits did not. |
| Self-hosted correlation | Exercise the framework's real HTTP path and concurrency; platform-specific hooks may not run in another hosting mode. | S3 records a real HTTP test exposing missing request-ID propagation and the local fix. |
| Config mounts | Verify effective container configuration after files are replaced, not just the host source. | S3 records a local change from individual file mounts to configuration-directory mounts; running production containers still needed an approved update. |
| Release boundaries | Monitoring setup and application deployment have different authority and evidence. | Proxy repair did not authorize restarting the app; production app telemetry remained pending in the source record. |

For the maintained diagnostic workflow and safe telemetry design, read
[observability and incidents](../../custom/skills/reliable-web-app-operations/references/observability-and-incidents.md)
and [deployment contracts](../../custom/skills/reliable-web-app-operations/references/deployment-contract.md).
Do not universally disable proxy buffering or loosen disk/permission limits based
on this case. Verify the same mechanism in the target first.

## Specialist reuse, not another agent library

The central [manifest](../../manifest.json) already selects UX Architect, UI
Designer, Frontend Developer, Software/Backend Architect, DevOps Automator, SRE,
Identity & Access Engineer, Application Security Engineer, Test Automation
Engineer and Reality Checker from the pinned original provider. Keep those roles
at their provider; do not copy Elvique's project-specific registry globally.

Select a lead for the actual risk, then only useful supporting reviewers. Pass
the target's approved business rules and evidence limitations, not Elvique's
assumptions. A role being installed is different from being invoked, and an agent
verdict is different from a passing browser, provider or deployment workflow.

## Source provenance and limits

Source project: `Elvique`. Baseline HEAD at review:
`1e0a94ef4ffbadc974325cc00fe930b7b76c0cc1`. The files below were **working-tree
documents**, not a clean snapshot at that commit. Hashes identify the exact
reviewed documents, not deployed artifacts. Raw files remain in the app.

| ID | Repository-relative source | State | SHA-256 |
| --- | --- | --- | --- |
| S1 | `AGENTS.md` | Modified tracked file | `e12c5e94961a59ed4b533f0c0e4a7c293c8579c49bb5f9461f1b27f74c09b8da` |
| S2 | `docs/21_REUSABLE_ENGINEERING_PLAYBOOK.md` | Untracked working-tree file | `a0e3c3d6ff293a6a46a26c51cb25101a017c26a06e210fcd8856d72ab9b4f204` |
| S3 | `observability/runbooks/2026-09-26-grafana-plugin-download.md` | Untracked working-tree incident report | `57c0aaedc1fd09597e4ee2a855b65129f4c9113751308e055c2a79cbe1b61acd` |

S1 is a requirement source, S2 a migration record, and S3 a recorded execution
report dated 26 September 2026. Reported checks were not repeated for this
publication; this case does not certify current production health, all business
flows, security or whole-site UI consistency. Graph metadata was stale or lacked
these documents, so this review read the files directly. Original discussions
and private test artifacts were not republished.

Locate raw evidence only within an authorized source workspace. Missing source
access is a limitation, not permission to clone private repositories. The case
and bundled skills remain usable without that checkout.

## Apply to the next project

```sh
ai-setup search "elvique observability"
ai-setup search "elvique admin UI"
ai-setup search "elvique architecture"
```

For each relevant lesson, state **adopt, adapt or reject**, why the target differs,
and the smallest test of the intended outcome. Keep those target decisions in
the target repository. Shared guidance reduces repeated discovery; it is not
automatic model training, guaranteed retrieval or proof of a better first run.
