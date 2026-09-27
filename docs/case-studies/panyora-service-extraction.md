# Panyora: service extraction, central CI/CD, security and QA

Reviewed: 27 September 2026. Type: curated engineering case study for cross-project
learning. Search terms: Panyora, microservices, monolith segregation, service
extraction, cicd, CI/CD, DevOps, gateway, database operations, security, QA,
containers, Docker, Kubernetes, versioning, hotfix, promotion, rollback.

This case preserves reusable decisions and failure lessons from local source
records. It is not Panyora's current architecture, operating runbook or deployment
approval. Original project docs remain authoritative. No services, CI jobs,
security probes or provider transactions were run to compile this case.

## Read before proposing another extraction

Use this case with the maintained skills:

- [Service architecture and extraction](../../custom/skills/service-architecture-and-extraction/SKILL.md)
  for boundaries, shared data and migration sequencing.
- [Reliable web app operations](../../custom/skills/reliable-web-app-operations/SKILL.md)
  for build, version, deployment and recovery contracts.
- [API documentation governance](../../custom/skills/api-docs-governance/SKILL.md)
  for service-owned contracts and cross-repository discovery.

Compare relevant decisions below with the target's actual code and requirements.
Record **adopt, adapt or reject**, the reason and the target's verification gate.
Do not copy repository counts, service names, cloud topology, provider assumptions
or rollout commands from the source project.

## What changed, and what stayed coupled

The extraction record describes moving authentication, subscription lifecycle,
provider transport and directory responsibilities behind explicit interfaces.
Transactional business state remained with its authority. Repository separation
did not imply physical database separation: the recorded stage retained one
PostgreSQL database, restricted runtime roles and explicit cross-domain reads.

Provider transport did not automatically become the financial ledger.
Authentication did not absorb every business membership operation. Existing UI
routes and selected compatibility adapters preserved consumers while ownership
moved. These are questions for another project, not a universal architecture. [S1]

Delivery evolved from source releases to centrally built containers, then hosted
releases and later deployment adapters. The early central build report says hosted
triggers were absent; the later hosted-release record reports activation. Reading
one historical report alone gives the wrong picture of the later setup. [S1–S4]

## Decisions and failures worth reusing

| Area | Concrete source lesson | Apply in another project | Evidence / limit |
| --- | --- | --- | --- |
| Service ownership | Identity, membership, entitlements and payment transport had different authorities. Core transaction boundaries survived extraction. | Map writes, invariants, credential owners and consumers before selecting repositories. Keep a coupled boundary explicit if splitting it would break atomicity. | S1 records implementation and demo checks; no independent-database or measured-scaling claim. |
| Central CI/CD builds | Ops owned one application Dockerfile, supported profiles, manifest validation and publishing. Apps owned code, ordinary scripts and a root runtime/build manifest. | If centralized CI/CD is required, apps declare inputs and ops owns execution. Separate service declarations from docs/tooling/DB-ops declarations. Test each supported runtime profile. | S2 records central builds; S3/S4 record later hosted execution. This ownership model is not mandatory for every small app. |
| Artifact identity | An ops-only build change could produce a different image for the same app revision. | Bind app SHA, build-platform SHA, manifest hash and image digest. Keep original build identity separate from later deployment executor and target identity. | S2/S4/S5; a published image is not deployment evidence. |
| Packaging failures | Runtime smoke tests found traced-module deletion and broken relative symlinks. A DB-dependent test initially blocked publishing. An install exited successfully with a missing optional compiler package. | Exercise HTTP, workers and migrations from the final image without development mounts. Declare unit versus DB integration checks; verify required installed tools. Bound recovery attempts and surface failures. | S2 records failures/fixes; the dependency transfer/extraction root cause remained unknown. |
| Credential capability | A configured source token still lacked Contents access. Cloud federation rejected an assumed subject format. | Verify the actual provider operation and identity claims, not secret presence alone. Separate source-read, release-write and deployment capabilities; keep deployment credentials out of app builds. | S3 records failures and subsequent hosted success. Destination account capabilities need fresh verification. |
| Versioning and hotfixes | Version calculation, release PR/tag publication, image build and deployment were separate. An explicit tag did not implement a maintenance branch. | Distinguish urgent main-based release from patching deployed code while excluding newer main features. Review the complete release diff and preserve a forward-port path. | S6/S7: main-based releases supported; isolated production hotfixes unimplemented in the reviewed record. |
| Immutable promotion | Later deployment selected a successful build run/attempt, validated retained artifacts and reused exact image digests. | Reject missing, expired or mismatched artifacts; do not silently rebuild or select latest. Test inspection separately from apply. | S5 records real artifact inspection and a hosted inspection run; that run did not deploy. |
| Worker/DB handover | Deployment drained a financial worker and coordinated backup/migration before switching services. Unsettled work kept scheduling paused. | Include schedulers, pending jobs, DB locks and migrations in the release. Roll back compatible code against current data; never overwrite accepted writes or blindly replay money movement. | S1/S5; successful handover and recovery tests differ from forced live failure/restore evidence. |
| Security regression | Direct routing to the extracted auth service bypassed a request-size guard in the old adapter. The fix checked actual streamed bytes and declared length. | Re-test controls at the new owner and public path: body bounds, raw bytes, origins, cookies, trusted headers, revocation and service credentials. Proxy protection does not prove direct-service protection. | S8 records the regression, fix and repeated local/public checks; not a whole-application security certification. |
| Runtime isolation | Inspection checked actual runtime DB roles and environment separation. Container hardening did not establish network isolation. | Verify running credentials and privileges. Separate nonroot/read-only execution, network policy, tenant/object authorization and secret distribution. | S2/S8 describe bounded observations, not a universal security guarantee. |
| QA evidence | Browser flows, local DB tests, denied-role requests and provider mocks supported different claims. Parallel browser runs collided in one output directory; login bursts hit legitimate throttling. | Use allowed and denied journeys with isolated fixtures/artifacts. Fix test orchestration without weakening security limits. Preserve failed attempts and skipped-case distinctions. | S1/S8; demo actions and mocks did not verify real settlement, refunds or email delivery. |
| Deployment portability | Compose and Kubernetes needed different discovery, secrets, job and recovery behavior. A selector did not migrate data or stop an old scheduler. | Find hardcoded loopback assumptions, provision the target, verify data connectivity and drain old jobs before cutover. Require target-specific runtime evidence. | S5: local adapter/rendering and hosted inspection evidence; new fleet/cluster deployment remained untested. |
| Documentation discovery | A docs entry point composed owner-maintained sources with revision/hash snapshots and a bounded operation inventory. | Keep contracts with owners; provide a small index with freshness/coverage limits. Generated route inventory is not reviewed authorization or automatically OpenAPI. | S9 describes an internal local artifact; publication/access controls are separate. |

For detailed reusable checks, read
[central builds](../../custom/skills/reliable-web-app-operations/references/central-container-builds.md),
[release/version/hotfix policy](../../custom/skills/reliable-web-app-operations/references/release-versioning-and-hotfixes.md),
[portable deployment](../../custom/skills/reliable-web-app-operations/references/portable-deployment.md)
and [security/QA](../../custom/skills/service-architecture-and-extraction/references/security-and-qa.md).

## Evidence boundaries

- **This review:** local tracked documents, Git revisions and clean file status.
  This synthesis is not a fresh implementation audit or infrastructure inspection.
- **Recorded execution:** extraction checks, single-VM container releases,
  selected hosted gateway/web releases and public demo browser journeys.
- **Recorded implementation/inspection:** additional deployment adapters and
  promotion inspection have separate evidence; they do not inherit the VM result.
- **Not established:** live financial transactions/delivery, a new fleet/cluster
  cutover, isolated maintenance-track hotfixes, general scaling gains or exhaustive
  security. Consult current owner docs before relying on an old result.

## Source map for an authorized reader

Sources were clean tracked files at review time. Ops source revision:
`panyora-ops@b0a6d5be83b6c0eeff4221bbaaede1e2a4164106`.
Docs source revision: `panyora-docs@bf60c0155d6dee768d77794509bd4f9501b74db8`.
These identify the documents, not necessarily the deployed implementation.

| ID | Repository-relative source | Read for |
| --- | --- | --- |
| S1 | `panyora-ops/docs/service-extraction-2026-09-27.md` | Boundaries, coupling, worker handover and early QA |
| S2 | `panyora-ops/docs/central-build-platform-release-2026-09-27.md` | Central manifests, packaging failures and container evidence |
| S3 | `panyora-ops/docs/hosted-release-setup-2026-09-27.md` | Credential/OIDC failures, recovery and recorded hosted results |
| S4 | `panyora-ops/docs/hosted-releases.md` | Later hosted pipeline ownership and operator gates |
| S5 | `panyora-ops/docs/deployment-targets.md` | Promotion, topology, recovery and untested targets |
| S6 | `panyora-ops/docs/app-versioning.md` | Versioning versus image build/deployment |
| S7 | `panyora-ops/docs/hotfixes.md` | Main-based release versus unimplemented isolated hotfixes |
| S8 | `panyora-ops/docs/security/extended-review-2026-09-27.md` | Extraction regression, security/QA scope and remaining conditions |
| S9 | `panyora-docs/README.md` | Owner-composed docs, snapshot checks and access limits |

Locate these within an already authorized Panyora workspace. Do not clone private
repositories or expose raw documents merely to follow a case reference. The case
and skill links work without source checkouts. If source access is missing, say so;
do not claim current Panyora verification. Original discussions were not inspected;
the reasoning here comes from the cited maintained records.

## Use from Servinoza or another project

```sh
ai-setup search "panyora microservices"
ai-setup search "panyora cicd"
ai-setup search "panyora security qa"
```

Open the returned case and relevant linked references. Explain which decisions to
adopt, adapt or reject, why the target differs, and what would prove the proposed
change works. Keep that target-specific assessment in the target's docs. Search
does not automatically read sibling projects or old conversations; retrieving
this case does not itself prove a better design.
