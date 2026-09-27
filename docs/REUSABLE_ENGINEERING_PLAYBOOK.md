# Reusable Engineering Playbook

Project-neutral lessons from application delivery and service extraction.
Detailed guidance travels with each skill in `custom/skills/`
and its global installation. Application specifications, architecture discussions
and release evidence stay in each application's own repository. Only reusable AI
learning belongs here; see the [central authoring policy](../config/CENTRAL_LIBRARY.md).

## Choose the relevant skill

For service extraction, central CI/CD, security and QA, first read the
[Panyora case study](case-studies/panyora-service-extraction.md). It preserves
concrete decisions, failures and evidence limits with source revisions, rather
than another generic checklist. Search by the origin and topic, then compare
adopt/adapt/reject decisions against the target project's requirements. Cases
are learning material; each project's current docs remain authoritative.

| Work | Primary skill | Add when relevant |
| --- | --- | --- |
| API contract ownership, docs publication and cross-repo navigation | [api-docs-governance](../custom/skills/api-docs-governance/SKILL.md) | API platform or developer tooling expertise |
| Domain boundaries, gateways and service extraction | [service-architecture-and-extraction](../custom/skills/service-architecture-and-extraction/SKILL.md) | Security, database, API or QA expertise |
| Setup, deployment, environment, monitoring and provider delivery | [reliable-web-app-operations](../custom/skills/reliable-web-app-operations/SKILL.md) | SRE, security or database expertise |
| Forms, admin workflows, tables, selectors, uploads and permissions | [build-usable-apps](../custom/skills/build-usable-apps/SKILL.md) | Frontend, accessibility or browser testing |
| Money, status, eligibility, hierarchy, corrections and historical documents | [auditable-business-workflows](../custom/skills/auditable-business-workflows/SKILL.md) | The actual domain, billing or database specialist |
| Active incident and causal investigation | [sre-incident-investigation](../custom/skills/sre-incident-investigation/SKILL.md) | Relevant service or infrastructure expertise |

For work across several areas, begin with the highest-risk behavior and load only
the additional guidance needed. Skills support the user's chosen task and existing
permissions; they do not authorize deployments, restarts, payments or publishing.

## Microservices, security, QA, DevOps and CI/CD coverage

Use this index to find the maintained lesson, rather than creating a second skill
or copying a project's runbook. These are reusable decision rules; they do not
certify an application's security or prove that a deployment backend was tested.

| Topic | Canonical guidance | Decisions and failures preserved |
| --- | --- | --- |
| Monolith to microservices | [Service boundaries](../custom/skills/service-architecture-and-extraction/references/boundaries-and-gateway.md) | Transaction authority, payment/PII boundaries, explicit shared ownership, independent builds; repo count is not isolation or scalability. |
| API gateway and centralized API docs | [Gateway boundaries](../custom/skills/service-architecture-and-extraction/references/boundaries-and-gateway.md), [API ownership](../custom/skills/api-docs-governance/references/ownership-and-publication.md) | Gateway versus ops ownership, service authorization, raw webhooks, forwarding trust, owner-maintained contracts and versioned central discovery. |
| Security and QA | [Security and QA](../custom/skills/service-architecture-and-extraction/references/security-and-qa.md) | Endpoint/actor matrix, tenant and field restrictions, direct-service bypass, streamed-body limits, actual browser workflows and separate evidence levels. |
| Central CI/CD and containers | [Container build contract](../custom/skills/reliable-web-app-operations/references/central-container-builds.md) | App manifests, shared build profiles, scoped credentials, runtime dependency closure, hardened images, size measurement and safe cleanup. |
| Versions and hotfixes | [Release versioning](../custom/skills/reliable-web-app-operations/references/release-versioning-and-hotfixes.md) | Independent versions, Git-generated short IDs, immutable provenance, release PRs, isolated patches and partial-publication recovery. |
| Compose, multiple VMs and Kubernetes CD | [Portable deployment](../custom/skills/reliable-web-app-operations/references/portable-deployment.md) | Placement/discovery, retained-artifact promotion, OIDC identity, durable deployment locks, worker draining and complete rollback scope. |
| DevOps cutover and cleanup | [Release and retirement](../custom/skills/reliable-web-app-operations/references/service-release-and-retirement.md) | Runtime ownership, explicit environment preservation, legacy dependency proof, compatible releases and data-preserving rollback. |
| Database operations | [Database lifecycle](../custom/skills/reliable-web-app-operations/references/database-operations.md) | Runtime resource versus repo, least-privilege roles, live schema checks, backup rotation, disposable restore and host migration. |
| Observability and incident response | [Operations telemetry](../custom/skills/reliable-web-app-operations/references/observability-and-incidents.md), [SRE investigation](../custom/skills/sre-incident-investigation/SKILL.md) | Layered evidence, safe logs, bounded metrics and causal investigation. |
| Parallel specialist work | [Agent briefs and acceptance](../custom/skills/service-architecture-and-extraction/references/agents-and-acceptance.md) | Bounded ownership, graph/source handoffs, contract coordination and independent review without duplicate discovery. |

When reporting that knowledge was shared, distinguish an edited canonical file,
a local commit, a verified remote commit and an installed consumer revision.
Check the remote branch contains the intended files before saying “published”.
Other machines require their normal authorized update; publication does not
automatically refresh their installed skills.

## Merge decisions

`operational-admin-ux` was merged into `build-usable-apps`: both guide application
workflow and operational UI work. Its tables/selectors, forms/uploads and
permissions/audit references are preserved and linked for selective reading.
No second skill or compatibility alias is installed under the former name.

Operations remains separate from SRE investigation. The former designs the release
and telemetry path; the latter establishes causes using incident evidence.
Combining them would bring unnecessary deployment instructions into read-only RCA.

Auditable workflows remains separate from UI and operations. It governs source
facts, derived values, rule versions, corrections and historical snapshots across
all consumers. A UI change need not load that domain guidance unless its business
behavior requires it.

The 27 September additions retain separate triggers: API docs governance owns
contract/discovery/publication decisions; service architecture owns boundaries
and extraction. Release/retirement and database operations are references within
`reliable-web-app-operations`, rather than additional overlapping skills. Versioning,
production hotfixes, artifact promotion and portable deployment also belong in its
selectively loaded references. Financial
authority across services stays in `auditable-business-workflows`. Load adjacent
guidance when the task crosses those responsibilities.

A local addendum to the provider-owned `testing-strategy` repeated the new
architecture skill's contract/actor checks, streamed-body limits, browser workflow
checks and separate evidence levels. That guidance is maintained in
`service-architecture-and-extraction/references/security-and-qa.md`; the installed
`testing-strategy` returns to its pinned provider version. Use both for a service
extraction test plan. This avoids keeping an untracked fork of provider content.

## Lessons preserved

1. Fix demonstrated shared causes across equivalent controls and consumers before
   claiming a global correction.
2. Separate source facts, derived values, projections and settled outcomes.
3. Treat referral, placement, access, participation, contribution, propagation and
   earning as distinct policies where the approved domain model uses them.
4. Distinguish provider acceptance, delivery and completion.
5. Preserve recoverable operator input and explicit deployment environment values.
6. Verify the changed workflow after build or deployment; health alone is insufficient.
7. Distinguish browser/network, proxy, application, storage, host and provider failures.
8. Keep realistic demo/test data isolated at the shared reporting boundary.
9. Make corrections explicit, impact-aware, authorized, atomic and auditable.
10. Keep reusable guidance project-neutral and business rules in project specifications.

The 27 September admin-access follow-up adds immediate elevation versus accepted
invitations, appropriate placement of privileged controls, unknown-account
handling and stale-session/action replay checks to `build-usable-apps`. Its
acceptance reference covers the same behavior across relevant roles and approval
states. `auditable-business-workflows` owns the accompanying QA financial
isolation and classification-transition guidance. These are reusable decision
rules, not a migration of private project architecture or proof of deployment.

## Install and maintain

Use the [custom skill catalog](../custom/skills/README.md#install-and-use) to install
the collection or share a complete individual folder. Supporting references install
with their skill. The `custom` component discovers these folders automatically on
macOS, Ubuntu/Debian and native Windows; no provider payload is vendored here.

Search with `ai-setup search "TOPIC"` and locate the source with `ai-setup library`.
Update the maintained source in `custom/skills/`, validate its frontmatter and
links, then apply it to the installed consumers only within the authorized scope.
Installed folders are managed copies, not parallel authoring locations. Preserve local edits if the
installer reports a conflict. Keep implementation, local checks, provider tests,
deployment and live completion as separate evidence levels.
