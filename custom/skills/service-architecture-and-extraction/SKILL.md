---
name: service-architecture-and-extraction
description: Assess service boundaries or extract a monolith into independently owned modules, repositories and deployments, including gateways, data ownership, migration and cross-service QA. Use for decomposition, multi-repo architecture, shared-directory cleanup and coordinated cutovers; not routine single-service features.
---

# Service Architecture and Extraction

Make ownership, runtime dependencies and release consequences explicit. Splitting repositories does not by itself create independent services, improve performance, isolate data or establish regulatory/IPO readiness. Preserve the user's actual business workflow throughout an authorized change.

## Scope and evidence

When the central `ai-setup` library is available, search for prior extraction cases
before selecting a design: `ai-setup search "service extraction"`, and search any
reference project the user names. The curated Panyora case is discoverable with
`ai-setup search "panyora microservices"`. Read its evidence and linked references;
state which decisions fit, need adaptation or should be rejected for this project.
Do not infer repository count, live readiness or business authority from analogy.

Use `ai-setup search "project catalog"` to locate current owner docs when borrowing
an existing implementation; verify relevant source/configuration and freshness
within authorized access. After a meaningful extraction or switch, follow the
central `"learning workflow"`: update the app's current operating picture and
preserve attempted approaches, failure/success evidence, reasons and superseding
decisions in the existing case. A pointer or old case is not current runtime proof.

1. Determine whether the request is an assessment, plan, implementation, deployment or cleanup. Honor existing authorization; a plan or reusable skill grants no additional deployment, deletion, provider-spending or source-publication permission.
2. Read applicable instructions and inspect the actual code, routes, contracts, configuration ownership, tests and runtime/deployment records. Prefer configured graph tools when required; verify project/generation/coverage and read missed source. Do not use unrelated graph matches simply because they contain words such as gateway or ops.
3. Record current, proposed, implemented and observed deployed architecture separately. Include workers, external providers, databases, uploads, caches, backups, secrets/configuration ownership and host infrastructure—not only repositories.
4. Preserve existing changes and consumers. Select the smallest boundaries that solve the stated team, context, scaling or security problem. A modular monolith, shared primary database with restricted roles, or coordinated release may be a valid interim design; label its limits.

## Design around authority

For each proposed component, identify responsibility, transaction/state authority, interface, consumers, data read/write privileges, configuration/secrets, resource lifecycle, tests and deployment owner. Distinguish module boundaries, repository boundaries, runtime processes and physical infrastructure.

Avoid repo-per-folder extraction and an unowned shared bucket. A shared library can be legitimate when it has a narrow purpose, owner, version, dependency policy and compatibility tests. Generic leftovers need classification, not cosmetic renaming.

For frontend consolidation, separate ordinary screen ownership from shared visual
foundations and backend authority. Assess direct workspace-source coupling versus
immutable published packages with exact consumer pins. Review ownership is not
directory-level access isolation; affected-consumer testing is not automatic
multi-app deployment. Read the frontend/package section in
[boundaries-and-gateway.md](references/boundaries-and-gateway.md) before promising
one-repo handoff or independent releases.

Preserve invariants that require atomicity. If a split crosses a transaction, design idempotency, concurrency, failure/compensation and reconciliation first; use an outbox or another mechanism only when the workflow needs it. Do not move authoritative money or stock state into a provider-transport wrapper merely because it handles payments.

Read [boundaries-and-gateway.md](references/boundaries-and-gateway.md) for decomposition, secrets/PII boundaries, gateway responsibilities and extraction sequencing.

## Execute and verify the authorized slice

For a user-selected VM → local images → Compose → CI/CD workflow, use the
[staged extraction → images → Compose → CI/CD sequence](references/staged-extraction-to-cicd.md).
First prove the separated application on its target VM with ordinary commands,
then build/push images on the user's chosen machine, verify Compose deployment,
and only then automate CI/CD. Other deployment targets and automation platforms
remain valid. Record and honor the selected sequence; do not provision later-stage
infrastructure while the earlier runtime gate is unmet.

- Establish the current working journey and regressions at boundaries likely to move. Extract one useful vertical slice; keep compatibility adapters explicitly owned and removable.
- Produce reproducible service artifacts from identified revisions. A consumer must not require an undeclared sibling source tree or retired parent checkout. Verify a clean checkout/build where that independence is claimed.
- Coordinate contracts, migrations and worker handover; preserve explicit operator configuration. Use the operations references below for release and recovery mechanics.
- Verify service behavior, cross-service authorization, public routing and the actual user workflow. Do not infer success from build counts, screenshots, health responses or mocked payments alone.
- Retire legacy paths only after the dependency proof, recovery preparation and authorized cleanup gate. Keep source migration, service stopping and data deletion distinct actions.

Read [security-and-qa.md](references/security-and-qa.md) for the security matrix, browser workflow checks and evidence levels. Read [agents-and-acceptance.md](references/agents-and-acceptance.md) for bounded specialist work and realistic forward tests.

## Reuse adjacent guidance

When available and relevant, use:

- `api-docs-governance`: contract authority, central discovery, versioned docs and AI navigation.
- `reliable-web-app-operations`: deployment/environment/provider workflow. Its `references/service-release-and-retirement.md` and `references/database-operations.md` cover multi-service rollout and DB lifecycle; `references/portable-deployment.md` covers central deployment adapters, topology manifests and artifact promotion.
- `auditable-business-workflows`: financial/operational invariants, corrections, immutable records and authority maps.

Do not require installing these skills to proceed. If unavailable, inspect the project's own runbooks and apply the same core checks: explicit owners, scoped credentials, compatible code/schema, verified backup/restore, controlled cutover and separately reported evidence. Use the existing browser/security tools appropriate to the task; availability does not authorize cloud scans, private-source uploads or production mutations.

## Deliverables proportional to the task

For substantial architecture work, provide an ownership map, current/target context or container diagram, deployment/data view, one important sequence/failure flow and staged acceptance gates. Diagrams describe actual dependencies and trust boundaries, not merely a list of proposed repos.

When deployment topology changes, distinguish app build/runtime declarations
from ops-owned placement, discovery, replicas and credential references. Include
the deployment controller, worker scheduler and DB-ops backup/restore boundary.
Changing a deployment selector does not migrate durable data, drain an old
scheduler or establish that existing images support remote service discovery.

For implementation, report changed owners/files, compatibility impact, exercised workflows, deployment state, recovery evidence and unresolved risks. Separate static, local runtime, public-path and real provider results. Never promise complete security, measured scaling gains or compliance based on repository structure.
