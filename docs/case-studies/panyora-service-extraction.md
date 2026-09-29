# Panyora: service extraction, central CI/CD, security and QA

Reviewed: 27 September 2026; extended 29 September 2026. Type: curated engineering case study for cross-project
learning. Search terms: Panyora, microservices, monolith segregation, service
extraction, cicd, CI/CD, DevOps, gateway, database operations, security, QA,
containers, Docker, Kubernetes, versioning, hotfix, promotion, rollback,
monolith to microservices, API gateway, DB ops, backups, shellless, catalogue review.

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

## Reuse map: lesson, owning skill and acceptance gate

This map is the entry point for another project's agent. Follow the linked
reference for the reusable procedure; keep that project's implementation and
runtime evidence with its owner.

| Work | Reusable reference | Target-specific proof |
| --- | --- | --- |
| Monolith boundaries, gateway, PII and payment separation | [Authority and gateway](../../custom/skills/service-architecture-and-extraction/references/boundaries-and-gateway.md) | Identify authoritative writes and credentials; preserve transactions; prove the normal journey without the retired parent checkout. |
| Central Dockerfile, root manifests, build executor and cleanup | [Central builds](../../custom/skills/reliable-web-app-operations/references/central-container-builds.md) | Build a declared app from identified revisions; exercise HTTP and job entrypoints inside the final image without source mounts. |
| SemVer, Git-derived tags and hotfixes | [Versioning and hotfixes](../../custom/skills/reliable-web-app-operations/references/release-versioning-and-hotfixes.md) | Bind version, source, platform and digest; test the actual release track rather than assuming a branch or tag implements one. |
| Compose on one/multiple hosts or Kubernetes | [Portable deployment](../../custom/skills/reliable-web-app-operations/references/portable-deployment.md) | Render and preflight the chosen target, discovery and secrets; exercise rollout/recovery there. A configuration flag is not migration evidence. |
| Database ownership, backups, retention and recovery | [Database operations](../../custom/skills/reliable-web-app-operations/references/database-operations.md) | Verify live role/schema, successful scheduled execution and a disposable restore; preserve data during code rollback. |
| Security and browser QA | [Security and QA](../../custom/skills/service-architecture-and-extraction/references/security-and-qa.md) | Exercise allowed and denied actors through public and direct-service boundaries; verify persisted outcomes and mobile controls. |
| Central API discovery and contract ownership | [API documentation governance](../../custom/skills/api-docs-governance/SKILL.md) | Trace a workflow to its owner, exact contract and tests; detect stale source snapshots. Route discovery alone is not authorization evidence. |

Adopt the ownership and verification rules; adapt the tooling and number of
services to the target. Reject blanket repo-per-folder extraction, an unowned
shared directory, automatic publication of private artifacts and claims that
microservices establish security, scaling or regulatory readiness.

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
| Database runtime ownership | DB tooling owned container/data paths, backup scheduling and guarded recovery; ordered domain migrations stayed with their existing authority. | Include stateful resources and recovery dependencies in diagrams, even when they have no HTTP route. A container name is not a repo or data owner. | S10 records local/VM relocation and disposable restores; no new runtime audit was performed for this extension. |
| Backup retention | Scheduled archives rotated only after successful dump validation/publication; protected release backups were kept separately. | Serialize lifecycle/backup/migration operations with compatible locks; failed backups must preserve older good copies. Keep off-host storage, roles and encryption keys in the recovery plan. | S10 distinguishes archive checks, isolated restore, timer execution and live failover. Five retained archives and a daily timer were project choices, not universal recovery guarantees. |
| Image hardening and size | A later release used a verified shellless base and a narrow job dependency closure instead of copying whole production dependency trees. | Probe the actual runtime UID, native dependencies, worker imports, entrypoints and health checks; measure image size separately from shared host disk usage. | S11 reports final-image and deployed probes. It does not establish zero vulnerabilities or future base-image eligibility. |

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
| S10 | `panyora-db-ops/README.md` | DB runtime ownership, daily successful-backup retention and guarded disposable recovery |
| S11 | `panyora-ops/docs/image-hardening-2026-09-27.md` | Later shellless packaging, actual runtime probes, size and Git-derived tag correction |

The 28 September extension read S10 at
`panyora-db-ops@14d9fcdc4f1c3a8f80bec9c97903627d89bb50a5` and S11 from
the same ops revision named above. These are maintained source records, not fresh
VM observations. S11 supersedes S2's early full-SHA human-readable tag description:
later tags use app version plus Git's own abbreviation, while full provenance and
digest-based deployment remain required.

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

## 28 September 2026: reviewed catalogue data and browser evidence

This later addition is a local implementation observation, separate from the
historical extraction evidence above. The reusable problem is preserving an
approved customer-facing record while staff propose new structured facts and
media. Product-specific design and rollout details stay in the owner's
`panyora-docs/docs/workflows/catalog-quality.md`.

- **Approach corrected:** checking a draft revision alone did not guarantee that
  published media matched the reviewed bytes if the approval path re-encoded the
  image. Preserve already-normalized media through an internal trusted path;
  never expose a client-controlled normalization bypass. Add byte-equality
  regressions for both new-record approval and edits.
- **Quantity lesson:** contents per sellable unit, quantity ordered and physical
  stock are separate facts. Reuse precise server-side rules across sales
  channels. A sale increment need not constrain a measured physical count.
  Photographs support a human review; they do not prove weight or live stock.
- **Review discovery:** a newest-first bounded history can hide old pending
  requests. Prioritize actionable oldest requests and disclose truncation. A
  mobile table that merely avoids page overflow can still hide the proposed
  value offscreen; inspect screenshots and stack current/proposed evidence when
  needed.
- **Observed browser failure and recovery:** initial dev-through-gateway checks
  could not hydrate while HMR requests failed. An unguarded auth form performed a
  native GET before hydration. Native POST plus readiness gating addressed the
  credential submission risk; isolated production builds then passed the actual
  owner/staff and commerce browser flows. HMR was an observed environmental
  correlation, not a completed gateway root-cause audit. Do not weaken product
  checks to make a development harness appear green.
- **Evidence and limits:** 43 focused core checks, seven workspace checks and
  local production-build browser flows passed; synthetic photo fixtures test
  transport/review mechanics only. No deployment, real product verification or
  live payment is established by this entry. Other projects must re-run their
  role, stale-revision, byte-integrity and responsive-review acceptance checks.

Provenance: 28 September 2026, uncommitted local changes above
`panyora-core@1f0ad880547d7ec820dda2ec94c29786511db844`.
Reviewed `src/modules/inventory/catalog-drafts.ts` SHA-256:
`67a93173afbd06526fb0aea92f63599271e7c278e7bac7b103c9799f0736363c`;
`tests/catalog.test.ts` SHA-256:
`53309e8deb995993f25fc807be37a6758ad66417a7119d6c09850f991ffd0285`.
These identify local source evidence, not a released or deployed revision.

## 28 September 2026: database backfill precision correction

- **Problem/attempt:** a staged database extraction decoded decimal JSON tokens
  as strings to avoid binary-float rounding. SQL numeric columns accepted those
  strings, but numbers nested in JSON documents changed type. The comparison used
  the same decoder and could falsely accept this result.
- **Observed correction:** independent review identified the shared-decoder
  failure; a nested high-precision-number regression failed. Exact Decimal
  decoding plus numeric-token encoding replaced the workaround. The rejected
  staged import was preserved in protected evidence and replaced only after
  fingerprint checks; the live source was untouched.
- **Verification/status:** corrected row comparisons, actual runtime credential
  denial, and independent PostgreSQL-side row digests after local and VM
  disposable restores passed. Containers/backfills remain staging targets;
  application authority has not switched. No real provider payment/refund was
  performed. This is migration-rehearsal evidence, not completed service or
  personal-data isolation.
- **Reuse:** adopt exact typed transport and an independent verification path.
  Do not infer success from matching row counts, two tools sharing one decoder,
  or healthy containers. Complete shared-lock/authorization/payment contracts
  and a final writer handoff before enabling a separated database.

Owner evidence: `panyora-docs/docs/database-separation-progress-2026-09-28.md` and
`panyora-db-ops/README.md`. The uncommitted DB-ops implementation was based on
`14d9fcdc4f1c3a8f80bec9c97903627d89bb50a5`; `migrate-domains.py` SHA-256 was
`9bd6bd1fb40ed5857ae639bbdd72a000367ce66fbd9614489c63b30df763c09c` and the
regression file `tests/test_domain_migration.py` SHA-256 was
`61a582cc8a55348c0688909fabf8d24d3cac00014da144df2c3256bb3bb14f27`.
Private dumps, identities, financial amounts and runtime credentials are retained
only with the application, not this library. See the amended database-operations
reference for the generic rule; applying this lesson elsewhere still requires
that project's own regression and recovery proof.

### Same-day follow-up: diagrams must distinguish staging from cutover

- **Problem:** the current architecture showed only the original database in its
  main diagram while a separate migration record described provisioned staging
  clusters. Broad implementation wording obscured the incomplete application
  handoff. An owner question exposed this communication and verification gap.
- **Correction:** the primary agent independently checked running service
  connection destinations and read-only database activity, alongside a specialist
  source review. Applications still used the original database; staged clusters
  existed without client connections at the observation time. The current
  diagrams now distinguish active traffic, completed point-in-time imports and
  intended future ownership. Historical design evidence remains labelled.
- **Evidence limits:** rendered diagrams and documentation checks passed; this
  review did not perform a writer cutover, rerun migration reconciliation or
  establish completed data isolation. An idle connection snapshot cannot prove
  a database has never been used. Detailed evidence stays in the owning app's
  architecture and migration-progress record named above.
- **Reuse gate:** independently reconcile each active database arrow with
  deployed connection configuration and actual activity, then exercise the
  affected workflow before claiming migration completion. Show staged resources
  explicitly and label imports as non-replicating when applicable. Agent summaries,
  container counts and health checks cannot substitute for this acceptance gate.

### Same-day follow-up: retry safety and sequence state

The finish review found that partial multi-target normalization could not resume,
one report filename could hide retry errors, and an existing container could be
accepted before role bootstrap had committed. Receipt-bound, read-only recovery
now verifies normalized/retained rows and access restrictions; independent phase
journals preserve uncertain commit outcomes. Provision retries verify extensions,
restricted roles, public revocations and real saved-credential authentication.
Actual retries passed locally and on the demo deployment without reapplying SQL.

The review also found that reconstructed identity sequences used surviving row
maxima, losing consumed/cached allocation state. New snapshots preserve options
and observe allocation state after the MVCC row snapshot; a final writer fence
is still required. Real PostgreSQL synthetic tests passed for nondefault options,
allocated high-water marks, descending and never-called sequences, exact next
values and mismatch rejection. Historical staging receipts remain unchanged and
do not inherit this new verification. Application cutover is still incomplete.

The revised DB-ops suite passed 78 unit tests. New implementation provenance above
the same base revision: `migrate-domains.py` SHA-256
`b002976fcabedb78d99dc1255c669e172235c4cb4b24e89ad27d225247cc2bbb`,
`normalize-domains.py` SHA-256
`fc847040a060dd07af4df86ac079ca12c3babd54e2eadacebf4245ca30d61e55`.
This supplements the earlier numeric-transport evidence rather than rewriting
it. No provider transaction or completed domain isolation is established.

## 28 September 2026: frontend handoff boundary correction

Historical proposal: its directly shared UI/token placement is superseded by the
approved release-boundary correction below. Keep the original reasoning as context.

- **Problem and earlier approach:** source extraction placed four frontend apps
  in separate repositories to accompany separate deployments. A later handoff
  requirement needed one frontend engineer to own the complete UI through one
  clone. Prior advice naming only two repositories did not cover all UI surfaces.
- **Observed evidence:** source review found repeated global styles and separate
  consumer contract versions. UI-side server rendering called backend APIs;
  this did not establish mixed database/business-backend ownership. Documentation
  from Next.js explicitly permits independently deployed zones in one repository.
- **Replacement/status:** propose a frontend-only monorepo with explicit app,
  UI-component, token and consumer-contract package ownership. Keep backend and
  platform responsibilities separate. This remains a researched proposal, not an
  implemented move or evidence that one repository is universally preferable.
- **Independent review:** central build/release code assumed one source repo and
  root package per runtime, root standalone output and repository-wide latest
  release selection. Consolidation therefore needs explicit app paths, workspace
  dependency builds, component version/tag lookup and provenance compatibility.
  Shared-package changes must select every affected app, not only changed app
  folders. Retain independent image rollback while changing source ownership.
- **Reuse and acceptance:** choose source boundaries for team collaboration and
  access needs separately from deployment units. A complete frontend handoff
  should support a fresh single clone and isolated design fixtures without backend
  source/secrets; integration still needs a development API and real workflow tests.
  Component stories are useful design evidence, not payment/security certification.

Owner proposal: `panyora-docs/docs/frontend-repository-design.md`, reviewed on
28 September 2026 against local worktrees above ops `b0a6d5b` and the four UI
revisions recorded there. Graph gaps were supplemented with current source reads.
Official pattern references: [Next.js multi-zones](https://nextjs.org/docs/app/guides/multi-zones),
[npm workspaces](https://docs.npmjs.com/cli/v11/using-npm/workspaces/), and
[Storybook](https://storybook.js.org/docs/get-started/why-storybook).
No source move, runtime change, Figma design or new monorepo build was performed.

## 28 September 2026: shared frontend package release boundary correction

- **Problem:** a single frontend clone helps screen work, but directly linked
  shared packages can affect multiple apps on their next build. More teams raised
  a legitimate ownership and release-containment concern; this was a design review,
  not evidence of a measured production incident caused by a monorepo.
- **Earlier approach:** the preceding proposal located common UI/tokens alongside
  four apps. It was not implemented. Preserve that proposal's reasons, but do not
  present its package placement as the active decision.
- **Replacement/status:** approved target is a frontend application monorepo plus
  a separately owned design-system repository, immutable package releases, exact
  per-app dependency pins and deliberate upgrade PRs. Ordinary screen work needs
  one clone; shared-foundation maintainers need another. Backend and platform
  ownership remains separate. No source consolidation or package publication has
  been performed by this documentation correction.
- **Controls and limits:** repository separation alone does not isolate consumers.
  CODEOWNERS with required reviews is governance, not directory permissions. A
  workspace package version field does not prevent source coupling. Consumer
  tests may run broadly; deployments remain individually approved. Root tooling,
  lockfiles, peer dependencies and global styles still need impact analysis.
- **Reuse:** adapt source boundaries to team/access needs, not traffic numbers.
  Keep generic visual foundations out of domain logic. Published packages may
  also be authored in a monorepo if explicit consumption boundaries are enforced;
  the additional repo is appropriate when permissions/maintenance warrant it.
- **Acceptance gates:** fresh consumer-only clone; two consumers resolve different
  package versions; candidate publication does not change existing apps; one
  upgrade promotes only one app; prior immutable image rollback; actual required
  review checks; security-fix adoption tracking. These are forward checks, not
  completed runtime evidence.
- **Provenance/evidence:** owner-approved decision on 28 September 2026 in
  `panyora-docs/docs/frontend-repository-design.md`; earlier source revisions and
  bounded inspection remain recorded there. Official GitHub CODEOWNERS and npm
  dependency documentation were rechecked. Current work updates application docs,
  this sanitized case and the existing service-architecture skill/reference only.
  No migration, enforcement configuration, deployment or scaling certification.

References: [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners),
[npm dependency specifications](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/).
Reusable guidance lives in `service-architecture-and-extraction` and its
`references/boundaries-and-gateway.md` frontend ownership section. This record is
maintained library content, not automatic distribution or guaranteed agent recall.

## 28 September 2026: implementing frontend release isolation

- **Implementation:** four committed UI baselines were consolidated into one
  frontend repository. Uncommitted feature work stayed in its original checkouts
  and was inventoried rather than silently released without matching backend work.
  A separate design-system source owns visual tokens and a generic button; private
  versioned release assets are consumed as checksummed vendor artifacts. Existing
  runtime identities remain separate. Central ops owns builds and package checks.
- **Release correction:** repository-wide latest-release lookup was replaced by
  component-specific stable tags, package paths and isolated pinned checkouts.
  Shared root dependency/configuration commits are classified for affected apps;
  their original commit identity/message remains intact. Broader testing does not
  authorize deploying every consumer. Root lock updates change only the selected
  app version. Hosted version automation produced four independent patch releases.
- **Runtime finding:** nested standalone output changed the cache path while the
  production image remained read-only. The assembler connects the nested cache
  to the existing writable mount with a relative symlink. Tests exercised cache
  writes, relocated assets/health and computed browser tokens, not merely builds.
- **Provider findings:** new private repository scopes were missing from dedicated
  source/release CI credentials; user-updated scopes allowed versioning to succeed.
  Branch protection was unavailable on the account's private-repository plan;
  ownership files must not be reported as enforced approval gates. Existing SSH
  push or personal CLI access did not establish dedicated CI-token access.
- **Package-check recovery:** Actions used the canonical remote URL without a
  `.git` suffix, exposing an overly strict source allowlist. Exact-owner URL
  variants now pass while other owners/hosts fail. Candidate package bytes then
  differed across packing environments, but npm retained the old same-path file
  dependency checksum. Only the disposable candidate lock entry is re-resolved;
  npm integrity checks and production artifacts remain unchanged. Publication
  rejects existing versions and verifies tag SHA rather than trusting `--target`
  to move an already-existing tag.
- **Deployment correction:** comparing a pinned tooling revision with the latest
  branch tip failed when main advanced during a successful image build. The
  uploader now freshly fetches the approved branch and checks pinned ancestry,
  preserving the exact archive SHA. Real Git fixtures reject unpublished commits,
  rewritten history and failed fetches. Source-owner changes also require updating
  fleet image verification and bounded cleanup, not only build labels.
- **Bootstrap parity failure:** the next deployment reached the host but its
  Python bootstrap still accepted only profile-only service declarations. The
  Node validator already handled nested app paths. Both now accept only exact
  approved layouts; regressions execute the actual bootstrap with new and legacy
  manifests and reject traversal/wrong owners. Test every validator in the
  deployment chain, including dependency-free bootstraps, using compatible fixtures.
- **Evidence boundary:** local consumer tests/typechecks/builds, platform tests,
  relocated HTTP/browser checks and hosted component release creation passed.
  Corrected hosted candidate-consumer validation passed without publication.
  Two deployment attempts exposed the tooling and bootstrap checks above; their
  corrected successor passed image publication and single-host deployment.
  Post-deployment checks verified public login/tenant isolation/admin journeys,
  cart interaction, existing invoice print handlers and actual non-root read-only
  cache writes. Unselected backends retained their start times. Original evidence
  and exact digests remain in the owner's migration record. No live provider
  payment, OS printer output, mixed-version rollout or rollback drill was exercised.

Provenance: owner records `panyora-docs/docs/frontend-repository-design.md`,
`panyora-frontend/docs/migration-2026-09-28.md` and ops migration evidence; source
baseline `7bc9622`, visual extraction `406592f`, central packaging `6cfd9f3`,
candidate/release follow-ups `ca49191`, `87dac59`, `dfe4121`, `daa3afa`, `b8beb6b`. This is a sanitized
engineering case, not an application runbook or distributed memory update.

## 28 September 2026: domain cutover rehearsals and compatibility

This extends the earlier staging-only database entry. Service contracts and local
application rehearsals are now implemented; the recorded demo deployment still
uses its original writer. Older staging observations remain historical evidence,
not current implementation blockers or proof of a completed live handoff.

- **Problem and approach:** separate authentication, personal data, payments,
  subscriptions and operational state while preserving existing users, documents
  and publication. A local source rehearsal passed domain migrations and guarded
  reference backfills, followed by application/browser checks. A second rehearsal
  used the actual deployed source schema because development already contained
  unreleased catalogue policy changes.
- **Observed failures and causes:** a reused cluster-wide role retained capability
  membership from an earlier rehearsal; the staging-denial check correctly stopped
  it. An identity login did not inherit its capability role's search path. Health
  checks also hardcoded runtime names rather than the intended capabilities.
  A dotenv line-splitting helper changed quoted key values, and ordinary local
  framework startup could load undeclared fallback credentials. Separately,
  persistent equality/idempotency hashes incorrectly depended on a bearer token
  intended for routine rotation.
- **Replacement/status:** each rehearsal receives new restricted logins, explicit
  per-login settings and domain grants after verified migration stages. Readiness
  retains real database/role/privilege/data checks while accepting the scoped
  principal. Private configuration uses the runtime parser and checks logical
  value preservation. Durable purpose-specific index/fingerprint keys are required
  independently of service tokens; rotation regressions protect stored hashes.
- **Compatibility decision:** the deployed source lacked the new approval fields.
  Rather than invent owner approval or hide previously published items, a guarded
  bridge records only verified existing publication revisions. Unknown contents
  remain unknown; new publication remains strict. Product changes or unpublishing
  retire the exemption. The historical quantity rule is retained only while its
  original eligibility remains valid. This is an explicit temporary policy, not a
  general bypass for missing metadata.
- **Data-minimization correction:** source review found private invoice notes
  duplicated in operational events. Exact matching notes reuse immutable invoice
  evidence; differing notes receive their own immutable evidence before removal.
  New events use a generic reference. This does not classify every arbitrary
  operational note or photo as free of personal data. A build of an old frontend
  repository was also rejected as release evidence; the feature delta and checks
  were moved to the actual deployed consumer.
- **Verification and limits:** isolated PostgreSQL tests, exact source/row checks,
  guarded/repeated backfills, authorization/key regressions, and local gateway
  catalogue, quote, photo and historical-invoice comparisons passed. Browser stock,
  POS invoice and demo renewal checks passed on the first rehearsal. In the actual
  source rehearsal, local fixture passwords did not match source hashes; imported
  sessions were validated using preserved signing material and a separate new
  synthetic account exercised password login. Original-password login was not
  claimed. No real payment/refund/settlement/email, final public deployment or
  production writer switch is established by these results.
- **Further acceptance correction:** catalogue quotes and owner invoices passed,
  but an existing customer receipt link failed under the real service role. A new
  invoice-line column had no privilege in the older source's explicitly exported
  column ACLs; the development source already had that grant. A narrow additive
  successor migration preserved the earlier checksum. The regression now proves
  denial before the grant, actual restricted-role read/insert afterward, and no
  update privilege. Existing customer links/invoices and invalid/cross-tenant
  capability denials subsequently passed. Source-specific ACLs and every affected
  consumer path must be in the acceptance matrix; a successful quote is not a
  successful receipt.
- **Build portability correction:** the first successor image build failed an
  exact gzip archive hash. macOS Node 22.22/zlib 1.2.12 and Linux Node
  22.23.3/zlib 1.3.1 produced identical decompressed tar bytes, including file
  contents and metadata, but different compression bytes. Core fix `f1369c7`
  pins the uncompressed tar hash and retains repeated-export checks; published
  consumer archives and their integrity checks remain unchanged. Targeted tests
  passed on both toolchains. This resolves the tested packaging defect, not the
  full hosted build or live cutover: the successor release was still pending at
  this checkpoint. Detailed run IDs and release identities stay in the app's
  private release draft and eventual owner record.
- **Reuse:** adopt source-specific rehearsals, authority-bound minimization and
  purpose-key separation. Adapt compatibility policies to the real earlier
  behavior, with reviewed expiry conditions. Reject auto-approval, permissive SQL
  stubs, reused privileged test roles and silent acceptance of unplanned writes.
  Final production import must use a new fenced source, not a rehearsal already
  modified by successful tests.

Reusable procedure: the
[database operations reference](../../custom/skills/reliable-web-app-operations/references/database-operations.md#independent-domain-cutover-rehearsals-and-compatibility).
Owner evidence: `panyora-docs/docs/database-separation-progress-2026-09-28.md`,
`panyora-docs/docs/runtime-acceptance-five-databases-2026-09-28.md`, and bounded
review `panyora-core/docs/database-boundary-review-2026-09-28.md`. Reviewed worktrees
were based on core `b53dda5` and DB-ops `2555ff8`; pending DB-ops personal-reference
helper SHA-256 `1548d2527aab10d5f6a43142fb48ca0667c95a9c1c223eb86c51541839c93a9f`
identifies that reviewed implementation. Private evidence stays with the app.
This sanitized update is canonical authoring content only; no automatic memory
ingestion, client update, commit or publication is implied.

### Later 28 September checkpoint: image execution and lock handoff

The actual frozen-source VM import exposed a nested-lock defect: the CLI held all
import target locks while normalization tried to acquire its own exclusive lock.
The guard stopped execution; it was not evidence of data corruption. DB-ops fix
`6d2bd16` retains locked import/preflight, releases those locks before normalization,
and lets each normalizer revalidate source/receipts under its own lock. A regression
executes the actual CLI boundary with real OS locks and proves both exclusion and
handoff. The resumed owner-image migrations/backfills then passed, followed by
restricted-principal/foreign-domain denial checks and five isolated restores with
cleanup. The image release became healthy and its first billing one-shot passed.
Expanded public workflows and final source/scheduler retirement were still pending
at this checkpoint; no live provider financial outcome is implied. Exact source,
image, restore and deployment evidence stays in the application's progress/runtime
acceptance records. This successor preserves the earlier local-only evidence rather
than relabeling it as a live test.

### Final 28 September checkpoint: bounded public acceptance

The successor deployment passed imported owner/employee/admin access and
cost/location/tenant restrictions, historical customer/subscription invoice
comparisons, existing customer capability links and invalid-token denial. A new
browser signup completed trial onboarding, stock entry, cash POS with replay and
manual pickup payment/fulfilment with replay, with the expected stock changes.
Imported sessions were validated; original imported password login was not tested.
New signup authentication was exercised. These were demo/manual ledger journeys,
not provider collection, refunds, settlement or email delivery.

The original database had no remaining clients and was stopped with data retained;
its old backup timer was disabled. Billing scheduling was restored and all five
domain backup jobs succeeded. All application and domain database containers
were healthy. This completes the bounded VM handoff, superseding the earlier
pending checkpoints without deleting their failure history. Normal development
cutover required its own verification, recorded below. The domains still share one host; forced
production recovery, independent-host resilience and broad performance/security
guarantees are not established by these results.

### Later normal-development checkpoint: preserved gateway configuration

The separate normal-local promotion installed five canonical databases and started
the owner/frontend builds. Scoped database identities and owner health passed,
but onboarding through the normal gateway failed while the direct owner worked.
The preserved gateway process still targeted backend/frontend ports from older
tests. Inspection of its actual launch environment exposed the mismatch; the
operator explicitly corrected those destinations and restarted the gateway.
The repeated normal-browser signup, trial, stock, cash POS/replay, pickup/manual
payment/replay and invoice flow passed, as did existing local demo password logins
and inventory reads. Old test listeners were retired after verification; the
original local database was stopped with data retained after its client count
reached zero. Original-password sign-in and business, subscription and inventory
reads passed again after the stop. These
manual/demo results do not establish provider collection or delivery. Reuse the
check for actual gateway upstreams and the failing public path, not an assumption
that the expected gateway port or green owner health proves correct routing.
Detailed run/port evidence stays in the application's acceptance record.

## 29 September 2026: a usable developer boundary needs a running workflow

- **Problem:** the frontend source had been consolidated, but separate UI ports
  did not route registration, browser API calls or server-rendered reads. A
  component preview and installation checks were insufficient handoff evidence.
  Existing showcase credentials also did not imply access to a new backend.
- **Replacement:** one local launcher consumes a versioned gateway artifact;
  frontend engineers use a dedicated synthetic shared backend with individual
  revocable environment access and ordinary owner/staff accounts. Backend
  engineers use an artifact-only sandbox, pinned peers and five independent
  synthetic databases, replacing only their assigned service. Shared visual
  source stays in its own Storybook; consumers still upgrade immutable packages.
- **Review corrections:** reject orphan Docker resources before labelling data
  fresh; verify environment identity before provisioning; constrain credential
  destinations; keep source listeners loopback; use per-environment cookie
  namespaces and exact filtering. Ports do not isolate cookies. A schema-only
  fresh bootstrap excludes tenant data and migration history, and does not prove
  that production migrations ran. A development API can share a TLS hostname
  while retaining separate signing keys, databases and provider settings.
- **Observed evidence:** clean frontend and design checkouts installed; component
  stories built; browser login preserved Secure/HttpOnly/SameSite; a stock change
  persisted after reload; hot reload used the same browser origin. A source-only
  backend replacement on macOS exercised dependent onboarding/profile writes,
  then restored the pinned image. A Linux-specific bridge remained untested.
- **Failed approach preserved:** a generated Postman collection was valid JSON
  but embedded an incorrectly escaped regular expression. HTTP requests could
  still succeed while pre-request scripts failed. Script compilation and actual
  runner execution replaced JSON-only confidence. The corrected runner passed
  sign-in/session/business/inventory/sign-out with its normal secure cookie jar;
  a rejected destination sent zero requests. This was a command-line runner
  check, not a desktop-client or live-payment test.
- **Another runtime trap:** passing Node's env-file flag into a Next development
  process was propagated through child options and rejected. Parsing a scoped
  environment file in the owner launcher and spawning Next with explicit
  environment values worked in the actual local replacement flow.
- **Reuse and limits:** test the permitted checkouts and the normal browser/client
  path, not only direct service health. Keep internal service credentials out of
  frontend handoffs; never attach arbitrary developer backend code to a shared
  environment with broad tokens. Local Docker administrators can inspect local
  synthetic containers; source ownership is not a host security boundary.

Provenance: owner records `panyora-frontend/docs/engineer-onboarding.md`,
`panyora-ops/development/README.md`, and
`panyora-docs/docs/developer-handoff-2026-09-29.md`; initial frontend source
`88a1d8e`, API runner correction `3045bdd`, gateway `4a419f8`, design catalogue
`43269ab`, identity `80bfc28`. Sanitized learning only; credentials and detailed
runtime evidence stay with the application. This entry does not certify future
images, every endpoint, provider transactions or production capacity.

### Later 29 September refinement: local mocks for everyday UI work

The shared synthetic backend solved real integration but still required remote
access and a complete service/database stack for ordinary screen work. The user
requested a frontend-only, database-free path. Keep the shared backend for real
integration; add a separately labelled local mock mode for the common UI loop.
The frontend owns synthetic JSON and bounded memory-only handlers, reached through
the same gateway by browser and server-rendered requests. Unsupported operations
fail explicitly and never fall back to a remote API. Each launcher uses its own
cookie namespace; restart/reset discards state. No new VM deployment is needed.

Observed checks: three owner logins and inventory screens worked through normal
UI forms; a quantity edit survived a page reload. A clean frontend-only source
export installed and started without an environment file or sibling backend
checkout. HTTP tests covered staff review, stale/replayed requests, reset,
foreign Host/Origin denial and unsupported checkout. External browser requests
were blocked during UI checks; the existing remote font failed and system-font
fallback rendered, so this is not a claim that every asset is locally bundled.

Two contract traps were corrected: root package hoisting can select a different
contract version from the actual consumer, so resolve from that app; and strict
NodeNext checking rejected extensionless imports in a package designed for a
bundler, so the fixture check uses the consumer's module-resolution convention.
Fixtures check published response types and commands use the published runtime
schema. These checks detect structural drift, not changed business policies.
Very distant fixed trial dates also produced implausible UI; the seed now sets
relative trial dates at startup/reset, covered by an HTTP regression.

Reuse this for UI teams that need fast isolated screen states. Keep real tests
for stock, tax, invoices, payment and authorization rules; do not recreate those
authorities in a mock server. Storefront fixtures in this bounded implementation
are static and do not track inventory mutations. Real financial operations and
unsupported flows require integrated mode. Maintained source/evidence:
`panyora-frontend/mocks/`, `docs/mock-development.md` and
`panyora-docs/docs/developer-handoff-2026-09-29.md`; frontend implementation
published as `13237af` on 29 September. This source publication does not deploy
mocks to a server or change the shared backend's verification status.

### Same-day correction: mock support must cover a coherent journey

- **Problem and attempted boundary:** the first bounded server correctly rejected
  unsupported routes, but Sales and subscription Billing were still reachable in
  the UI. Their first API request fell through to the generic 501. Explicit failure
  prevented accidental remote access, yet the frontend handoff still advertised
  workflows that a frontend engineer could not exercise.
- **Replacement/status:** support is now described by workflow slices rather than
  route count. The local server handles POS read, preview, post, history, owner
  review, recorded-payment display and related in-memory loose-stock movement. It
  also handles owner-only demo subscription invoice issue, detail and simulated
  receipt. Published consumer schemas validate commands. Documents say demo and
  no real provider, database or remote fallback is involved.
- **Verification:** the new API regressions failed against the earlier fallback,
  then passed for preview/post/readback, stock reduction, tenant/role denial and
  demo invoice issue/read/simulated payment. The complete frontend test suite,
  all workspace typechecks and four production builds passed. A real browser used
  the single local origin to sign in, issue a customer invoice, observe updated
  stock, create a subscription invoice and simulate its payment. Console output
  contained development/HMR messages only.
- **Limits and reuse:** these checks establish frontend simulation behavior, not
  backend authorization, durable accounting, GST correctness, Razorpay activity,
  email delivery or settlement. For another app, inventory every user-visible
  local-mode journey and test its ordinary mutation plus refresh/detail outcome.
  Keep unsupported authorities explicit; do not make a shallow route stub appear
  usable merely because its initial page renders.

Provenance: `panyora-frontend@335533f`, published 29 September 2026. Reviewed
owner paths: `mocks/server.mjs`, `mocks/contracts.mjs`,
`tests/mock-api.test.mjs`, `mocks/README.md` and `docs/mock-development.md`.
This is source and local browser evidence; the mock server was not deployed.

### Later 29 September decision: environment lanes need immutable UAT identity

The product owner selected four logical delivery environments: an isolated
backend sandbox for a custom/feature PR into `stg`, shared integration from the
`stg` branch, UAT from the `stg` to `main` PR, and production from `main` through
canary and full promotion. Frontend-only work normally keeps the faster local
mock path; it needs a per-PR environment only when matching unreleased backend
behavior is material.

The frontend environment rule was made explicit: Staging is the default remote
backend after producer changes merge; the matching Development SSI is an
exception for unreleased backend integration. UAT is stable, time-bounded access
for release-candidate verification or defect reproduction. Production is not a
development target and exposes only approved observability/support paths. URLs,
synthetic accounts and scoped diagnostics do not imply database, VM, Docker or
internal-service access.

The important correction was that a UAT environment named after a moving branch
does not identify what QA approved. Bind approval to the PR number and exact head
SHA, complete service source/image-digest set, deployment configuration identity
and reviewed migrations. Any candidate change dismisses approval and requires
redeployment and repeated acceptance. Production promotes the approved digests
without rebuilding. For a multi-repository product, an ops-owned release manifest
is the compatible system candidate rather than the independent branch tips.

This was an architecture/documentation decision on 29 September 2026. Existing
Panyora hosted workflows were still manual and `main`-only when recorded; no
per-PR provisioning, staging/UAT deployment, branch protection, approval-reset
or production canary run was performed for this entry. Reuse the identity and
evidence rule, not Panyora's branch names. Verify the target provider actually
invalidates stale approval and promotes the same artifact digests before calling
the model implemented.

## 29 September 2026: Node's event loop is not pod autoscaling

- **Problem and hypothesis:** a future-scale review assumed that a Node pod could
  not use more than one CPU and that an event-driven Node stack scaled itself.
  This combined the single JavaScript event loop, distributed application events
  and orchestrator replica control into one mechanism.
- **Observed configuration:** the reviewed Kubernetes renderer allowed a two-CPU
  container limit while its examples declared fixed replica counts. No HPA,
  Node cluster/worker-thread process model or measured load result was found in
  the reviewed scope. Owner documentation already warned that horizontal replica
  gains, connection budgets and lock contention remained unverified. The demo
  topology and staged multi-database work did not establish production capacity.
- **Correction and decision:** a Node process normally runs JavaScript callbacks
  on one main event-loop thread, but its pod may use additional CPU for runtime,
  native and explicit worker work. For I/O-heavy APIs, retain Node/TypeScript and
  prefer one request process per container with horizontal replicas. Isolate
  demonstrated CPU-heavy work in bounded workers or a separately benchmarked
  service. Treat Next.js as a frontend/server-rendering choice rather than proof
  that every high-throughput API should use its route runtime.
- **Scaling gate:** classify cacheable edge traffic, origin reads, authoritative
  writes and background events before accepting an aggregate RPS target. Exercise
  a representative authenticated endpoint at one, two, four and eight replicas;
  record requests per allocated CPU, p95/p99, event-loop delay/utilization,
  memory/GC, database-pool wait and connection totals, errors and cost. Then test
  autoscaler burst/recovery, graceful drain, queue replay and dependency failure.
  CPU-only autoscaling and a health response are insufficient.
- **Data and event limit:** replica count multiplies connection pools and can move
  the bottleneck to PostgreSQL while Node CPU stays low. Budget total connections
  and verify lock/transaction behavior. Keep authoritative stock and payment
  transitions transactional; use events for asynchronous consequences only with
  ordering, idempotency, backpressure, replay and reconciliation.
- **Status and reuse:** this is an adopted architecture decision framework and a
  current-state configuration review, not a load test, HPA implementation or
  million-RPS certification. Reuse the distinction between process concurrency,
  messages and platform scaling. Choose another runtime for a hot path only after
  a like-for-like benchmark using its real database and validation contract.

Provenance: reviewed owner files on 29 September 2026:
`panyora-ops/cd/adapters/kubernetes.mjs`,
`panyora-ops/cd/examples/kubernetes.yaml`,
`panyora-ops/cd/environment.mjs`, `panyora-docs/docs/architecture.md`,
`panyora-docs/docs/database-separation-progress-2026-09-28.md` and
`panyora-gateway/README.md`. Source/configuration review only; no representative
load, live Kubernetes autoscaling or production capacity test was performed.

## 29 September 2026: one frontend origin passed routing, not full mock coverage

- **Question tested:** whether four independently running frontend applications
  could be used from one browser address without engineers switching ports.
- **Observed routing:** the actual root mock launcher started one loopback gateway
  and four Next.js workers. A real browser stayed on the shared origin through
  web home, login, authenticated workspace and storefront pages. Direct route
  probes mapped `/` to web, `/login` to workspace, `/shop/mock-s1` to storefront,
  `/admin` to admin and `/api/ui/session` to the API proxy. Six focused launcher
  tests passed, including shared SSR/browser origin and credential isolation.
- **Important distinction:** the signed-in mock owner received the intended 404
  from the platform-admin application, which established routing and role denial,
  not a usable admin workflow. Workspace Online Store management reached its UI
  but displayed the explicit integrated-only API message. The standalone mock
  storefront catalogue rendered successfully. Therefore all four processes were
  reachable, while local mock mode still did not support every user journey.
- **Configuration correction:** the documented default group was 3110–3114, but
  the reviewed local environment overrode it to 3610–3614. A process-level
  override was used to exercise the exact 3110–3114 group. Handoff instructions
  should treat the launcher's printed public URL as effective truth and keep all
  worker ports as implementation details.
- **Reuse and acceptance gate:** report shared-origin routing, authorization and
  workflow support separately. For each advertised app, navigate through an
  ordinary UI link where available, confirm the browser origin never changes,
  inspect asset/API routing and exercise an allowed and denied role. Inventory
  workflows supported by mock mode; label complete integrated-only journeys
  before entry rather than implying that process reachability makes them usable.

Provenance: local source/runtime review of `panyora-frontend` on 29 September
2026. Reviewed `scripts/development.mjs`, its pinned development-gateway package,
launcher tests and handoff docs; exercised the real mock launcher and browser.
No integrated backend credential, platform-admin session, provider operation or
production gateway was tested. This is local developer-routing evidence only.

## 29 September 2026: accumulated notes were not usable frontend documentation

- **Problem:** current setup, security boundaries, historical migration evidence,
  runtime observations and repeated caveats had accumulated in the same README
  and handoff files. Facts were mostly present, but the common install/run/test
  journey was hard to scan and the same limitations appeared in several places.
- **Replacement:** current frontend documentation was reorganized by reader task.
  The root README became the shortest start path and application map; a docs index
  routes to development, onboarding, mock, API and ownership guides; four app
  READMEs use the same compact reference structure. Dated migration and product
  research stayed intact and were labelled as historical evidence.
- **Observed result:** twelve current documents passed local-link, anchor, H1,
  command-presence, Prettier and diff checks. Twenty-one root tests, five workspace
  tests, four typechecks and four production builds passed. The current-doc set
  fell from about 6,900 words to about 4,450 while adding the index. This is source
  and build evidence; no external developer usability study was performed.
- **Reuse:** do not use README files as chronological evidence stores. Separate
  tutorial/quick start, task how-to, factual reference and explanatory history.
  Keep security constraints near the action they govern, link each current doc
  from one entry point, and verify commands and links mechanically. Preserve dated
  evidence rather than deleting it merely to make current docs shorter.

Provenance: `panyora-frontend@44e9749`, published 29 September 2026. Rewritten
current paths are `README.md`, `docs/README.md`, development/onboarding/mock/API/
ownership guides, `mocks/README.md` and four `apps/*/README.md` files. The
documentation was not tested by a newly onboarded engineer when this central
lesson was recorded.

### Same-day correction: dated files need a lifecycle decision

The first documentation pass kept every dated migration and research file. A
subsequent all-repository audit showed that this was too broad: completed
transition diaries and handoffs still appeared beside current guidance, while
retired UI repositories held editable copies of documents already owned by the
active frontend repository.

The correction classified tracked documents as current guidance, retained
decision/release/security/recovery evidence, superseded transition material or
duplicate content. Transition-only files and duplicate copies were removed only
after confirming current facts had an owner and Git retained the history. Active
runbooks, security evidence, database acceptance evidence and product research
were preserved. The first isolated audits missed links from other repositories;
a workspace-wide tracked-Markdown check then found and repaired both inbound
links to retired repositories and relative links broken by the deeper canonical
location.

Reuse the lifecycle classification rather than deleting files because their names
contain dates. Validate the final documentation graph across the whole authorized
workspace, not merely each changed repository. The source audit covered all 16
Panyora repositories; 25 obsolete or duplicate documents were removed across
nine repositories. Link and diff checks passed, alongside the affected frontend,
core-unit, subscriptions, docs and ops test suites. Core environment acceptance
was not rerun because its required cutover environment was unavailable; this was
a documentation maintenance change, not runtime cutover evidence.

Provenance: pushed source revisions `panyora-frontend@163378d`,
`panyora-core@4746eb3`, `panyora-docs@1ea8a14`, `panyora-ops@c870b67`,
`panyora-admin@363c2ea`, `panyora-web@2925962`,
`panyora-workspace@beb582b`, `panyora-storefront@7097531` and
`panyora-subscriptions@0874c34`, reviewed 29 September 2026. Git history is the
historical source for removed files; current application documentation remains
authoritative for present behavior.

## 29 September 2026: preserve live invariants when editing a partial draft

- **Problem and context:** a reviewed product editor accepted a draft payload
  whose pack records intentionally omitted live `locked` metadata. It also
  rendered every counted product with the UI default quantity step of `1`, even
  when the approved record used a valid whole-number step such as 2, 6 or 12.
  Saving either form could present an impossible edit or silently replace an
  existing business rule.
- **Approach that passed insufficient checks:** the original catalogue port had
  unit checks, typechecks, production builds and browser coverage for the common
  step-of-one journey. Those checks did not include a counted product with a
  non-default step or a draft editing a pack already used by stock history.
  Independent source review found both gaps before this release.
- **Demonstrated cause:** the form treated a partial proposal as a complete live
  aggregate. The draft contract had no `locked` field, and the component did not
  rejoin it with the current product pack by stable ID. Separately, the rendered
  input chose a type default instead of the matching approved detail value.
- **Replacement:** use draft fields for proposed values and rejoin omitted
  authority metadata from the current aggregate. Preserve the approved quantity
  step when its kind still matches; use creation defaults only for a new item or
  an explicit kind change. Keep the server as the final invariant authority.
- **Verification:** focused regressions now cover a counted step of 12 and a
  draft pack whose live counterpart is locked. The active frontend passed 21 root
  tests, nine workspace checks, all four typechecks and all four production
  builds. Preserved standalone workspace/storefront checks also passed. These are
  source/build checks; no provider transaction or production deployment was run.
- **Reuse:** whenever a draft, patch or projection omits fields, classify each
  omitted field as defaultable, immutable, derived or authority-owned. Rejoin
  authority-owned constraints by stable identity before rendering edit controls.
  Add regressions using valid non-default values; a default-only fixture cannot
  prove preservation.

Provenance: active source `panyora-frontend@0ea3829`; preserved-source commits
`panyora-workspace@696f814` and `panyora-storefront@45fc9b8`; workflow/status docs
`panyora-docs@2c52531`. All were pushed on 29 September 2026. The central lesson
does not make the preserved UI repositories active release owners.
