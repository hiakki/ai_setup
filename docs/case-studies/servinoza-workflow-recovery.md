# Servinoza: state transitions, recovery and rendered QA

## 28 September correction: inventory and source gate before further rollout

The operator stopped an overlapping extraction/deployment effort and requested a
clear sequence: document every API, assign owners, finish code separation locally,
push/deploy ordinary services, test the operation matrix, then repair and redeploy
only the responsible component. Earlier service builds and selected passing
journeys did not establish complete operation coverage or retirement readiness.

The replacement updates the application's existing `servinoza-docs/MIGRATION_EXECUTION.md`
and links an endpoint inventory and acceptance matrix. Keep this a **process
correction under implementation**, not a claim that the migration or all API tests
have passed. Preserve useful code and deployed services, freeze a compatible source
set before the next rollout, and report source/push/runtime/acceptance separately.
Re-test both owner and Gateway controls; the Panyora case's lost adapter guard is
a specific reason to include both boundaries. No elapsed-time attribution or
complete security claim was established by this review.

Reusable guidance is in the existing
[staged extraction reference](../../custom/skills/service-architecture-and-extraction/references/staged-extraction-to-cicd.md).
This addition records the operator's correction and reviewed plan on 28 September
2026; private endpoint inventories, account data and deployment details remain in
the application repository. Initial Hindsight discovery failed; a read-only MCP
connection subsequently authenticated and recalled reviewed extraction lessons.
Relevant retrieved excerpts were checked against their canonical case files;
unrelated hits were ignored. Recall does not verify current application behavior.
No memory write or library publication is implied.

Reviewed: 28 September 2026. Search terms: Servinoza, Servinoza_in, onboarding,
admin UX, recovery, approval, hold, payment, tables, responsive QA, cancellation.

This sanitized case derives from the application's consolidated correction
record. It preserves failures and decision criteria, not the application's
commercial terms, required identity documents or operating procedures. Original
decisions and release evidence remain in the source project. No application or
provider flow was rerun for the original document review. The dated extraction
addendum below has its own observed runtime evidence and limits.

## Decisions worth transferring

| Trigger in the source record | Reusable action | Verification and limits |
| --- | --- | --- |
| An action labelled Restore called approval, trapping an incomplete held account behind approval prerequisites. | Define removing a hold separately from granting approval. Match the label, server transition and next available task. | Exercise recovery with incomplete evidence, not only successful approval. The source records the correction; this review does not establish its current deployment. |
| Accepting a visit also committed a price before inspection. | Separate initial estimate, accepted visit, proposed scope/price, agreement and verified payment. Preserve earlier facts and resume at the saved stage. | Test refresh, stale tabs, failed/pending payment and attempted edits to paid scope. Source records a correction; real money movement needs separate evidence. |
| A paid screen still said to wait for payment because two controls received different relation/context data. | Derive messages and enabled actions from the same authoritative context. | Check both the correct message and absence of contradictory guidance in the paid state. A resting screenshot or typecheck missed this failure. |
| A table had no page overflow but its primary actions were hidden beside a tablet sidebar. Header cell edges aligned while padded text did not. | Base responsive decisions on available container width; measure visible task controls and rendered text, not just rectangles. | Inspect sorting, wrapped labels, hover padding, focus, modal open/close and compact layouts. The source records local and live table checks, with populated held/flagged cases only in local fixtures. |
| Pending search responses replaced current input; failed actions hid errors behind a modal. | Preserve the current draft across asynchronous responses and put failures within the active interaction. | Use delayed responses and rejected mutations; verify focus handoff and a usable retry. A successful fast response cannot cover these states. |
| Cancellation and replacing a professional were represented by ambiguous actions. | Separate ending the task from changing its future assignee. Snapshot accepted terms and retain the historical owner of work and receipts. | Test stale previews, repeat replacements and both before/after-payment paths. The consolidated record describes design and linked implementation evidence; do not infer every path was verified live. |
| An email-first recovery proposal coexisted with an implemented flow whose first durable save happened later. | Describe the actual persistence boundary. Distinguish sending a code, verifying it, creating an account and saving a draft. | Leave and return at each real boundary. A proposal is not an existing capability; SMTP acceptance is not inbox delivery. |
| A pending onboarding edit invalidated one submitted check and exposed superseded versions, stale errors and audit history as extra admin work. A first repair refreshed the UI after a stale response but resent a client-pinned submission ID, producing an endless reload/reject loop. | Treat pre-approval onboarding as one replaceable latest snapshot. Let the admin approve the current required snapshot and account in one transition; resolve that snapshot under the server-side review lock instead of using a rendered ID as the authority. Keep older versions in the audit store, outside the normal review UI. After approval, route protected-field changes through an explicit correction flow. | Test edits before approval, a rendered older ID resolving to the latest submission, optional legacy records, a real concurrent edit while approval is open, and protected edits after approval. Verify expired or missing evidence remains a distinct blocking state. A UI refresh alone does not repair a stale mutation contract. |

These patterns apply to many approval, booking and administration systems. They
do not mandate this project's roles, payment provider, document collection or
review policy. Simplify presentation only after preserving the underlying facts.

## Use the maintained guidance

- [Build usable apps](../../custom/skills/build-usable-apps/SKILL.md): state models,
  resumable tasks and browser acceptance.
- [Auditable business workflows](../../custom/skills/auditable-business-workflows/SKILL.md):
  accepted terms, corrections, historical ownership and financial isolation.

Search `ai-setup search "servinoza recovery"`. For the target, record which
lesson to adopt, adapt or reject and the test that would establish the outcome.
Keep the target's decisions in its own repository.

## Extracted-service test dependency follow-up

A later mail-integration guide requires an explicitly selected, versioned service
artifact with its built output and runtime dependencies. The parent test does not
silently discover ignored sibling directories, build another repo or treat a
missing artifact as a passed/skipped integration. This keeps a clean checkout's
capabilities distinct from one developer's workspace.

The guide describes exercising the real parent adapter with a compiled service
and temporary loopback SMTP fixture. Acceptance validates the expected operation
identity as well as response status; a plausible but wrong identity remains
uncertain without automatic fallback to a second delivery path. Stable business
operation keys are needed for cross-call deduplication; independent one-shot calls
cannot inherit that guarantee.

Source: `Servinoza_in/tests/README-mail-integration.md`, read in full, clean at
`603ec02d3ed783ca9242e25e6a4f13db3e96baef`, SHA-256
`99bacb76bfcaa45a69dd6e2b834be6d4f55664e845a762d18f14cf3ebb5fb955`.
This is a documented integration contract, not a test execution log or production
delivery result. No service was built, launched or messaged by this review.

## Authentication and release follow-up

A separate review distinguishes internal helper preconditions from authenticated
network boundaries. During extraction, a caller-supplied actor identifier does
not prove caller identity. Long-lived streams also need revocation/expiry checks
after connection; authenticating the initial request alone leaves an access gap.
Legacy actions must share current admission rules, and trusted client-address
headers must match the actual ingress contract.

The report preserves initial findings, then records remediation and a later
release separately. It describes real local HTTP revocation checks with disposable
data and public anonymous-denial checks after deployment, not live authenticated
financial operations. An API-method inventory still did not cover Server Actions
or certify future service-to-service trust. Retain these separate acceptance
boundaries when borrowing its security approach.

Source: `Servinoza_in/docs/qa/2026-09-27-auth-segregation-review.md`, clean at
`603ec02d3ed783ca9242e25e6a4f13db3e96baef`, SHA-256
`cdb48d1b533ac2b64a2999a6f1fbb9338c645261006624a28847a8d291a26176`.
Reviewed findings, verification, remediation and release sections; the route table
was not reproduced. This is historical report evidence, not a fresh security scan.

## Original source and evidence boundaries

Source: `Servinoza_in/docs/architecture/UX_LESSONS_AND_REUSABLE_SKILL.md`.
The record was consolidated on 25 September and includes later dated amendments.
It distinguishes earlier attributed reports from directly checked table release
evidence. A later correction does not make an earlier passing review comprehensive.

Baseline repository HEAD: `b05d2212f9e5041c8617e132c2b94b71a54ef8dc`.
The source was **modified in the working tree**, so HEAD is not its content identity.
Reviewed SHA-256: `10e263f3c1ba188164a2230f57ad5b15ec002915078b580aa050f688018e2b1c`.
Graph coverage reported changed metadata; the source was read directly in full.

This is a document synthesis, not a fresh implementation, security, accessibility
or financial audit. No private media, account records or original conversations
are included. Follow linked owner records in an authorized checkout for current
release status; this case remains usable without that private access.

## 30 September follow-up: resumable signup needs a reconstructable key

**Problem and failed approach.** A resumable signup stored its cooldown and safe
destination under an email-specific browser key. After refresh, the form no
longer knew that email, so it could not find the otherwise valid recovery state.
Early browser tests hid the defect by manually re-entering the email after reload.
Another early repair cleared the visible resume action before a resend completed,
so a throttled or temporarily failed request stranded the user on the same page.

**Replacement and status.** The recovery record now includes a bounded pointer to
the normalized lookup email as well as an allowlisted destination. Transient
429/5xx/network failures preserve the last confirmed recovery action. Successful
resume, successful ordinary signup, and the owner's definitive completed-account
response clear both the pointer and per-email state. This was adopted in source;
application release and production evidence remain with the application owner.

**Verification and reuse.** Component-browser regressions reload without manually
reconstructing form state, retry after throttling and temporary failure, and model
completion in another session. The broader rendered onboarding suite and a
production build also passed in the source review. These are local synthetic owner
responses, not proof of email delivery or a deployed customer journey. For any
resumable task, persist enough non-secret state to rediscover the authoritative
draft, preserve it across uncertain failures, clear it on terminal transitions,
and ensure the test performs the same reload a user does.

Source reviewed 30 September 2026: current Servinoza frontend, Accounts,
Verification and application decision docs in their owner repositories. Private
account data and release identifiers are intentionally omitted.

## 28 September addendum: staged extraction and journal ingestion

**Problem and approach tried.** Service extraction initially advanced toward image
and CI machinery before the separated ordinary processes were proven. The operator
selected a staged sequence: ordinary services, local image builds, Compose, then
automation. Existing later-stage source was retained as deferred work. Application
docs distinguish deployed owners from the still-required compatibility host.

**Why the replacement matters.** Clean detached service builds exposed undeclared
parent dependencies; live probes separated restricted database grants, user
journeys and worker ownership. A normal API deployment did not replace its
background scheduler. The migration remains partial; this is not a completed
microservice, independent-database or CI/CD claim.

**Failed monitoring check.** A candidate collector configuration validated, loaded
and reported ready with mounted host journals. Synthetic traces reached the trace
backend, but journal line counters remained zero and no matching logs appeared.
The candidate was rolled back and replaced with explicit journal-directory
selection while retaining exact worker filters and the existing curated pipeline.
Both synthetic log records then correlated with their traces. Other monitoring
services stayed unchanged. This supports the directory-selection repair in the
tested Alloy v1.19.2 deployment; it does not establish a universal container cause.

**Reuse and limits.** Follow the target operator's stage order; use isolated
artifacts, preserve transaction authority and verify the actual public journey.
Before worker handover, prove both scheduler fencing and telemetry ingestion.
Collector readiness, mounted files and valid syntax are insufficient. A synthetic
probe must not invoke financial work and is not evidence of normal scheduled
batch success, delivery, settlement or provider recovery.

**Provenance and successor pointers.** Current application migration evidence is
owned by `servinoza-docs/MIGRATION_EXECUTION.md` (revision `083e5b9` at this
observation); collector attempt, rollback and replacement evidence is in
`servinoza-ops/docs/WORKER_HANDOVER_REVIEW.md` (revision `4bfd74c`). Older parent
records above remain historical evidence. Current releases may advance; resolve
those owners before reuse. No customer records, infrastructure credentials or raw
release logs are included here.

The generic rules are maintained in
[staged extraction](../../custom/skills/service-architecture-and-extraction/references/staged-extraction-to-cicd.md)
and [observability checks](../../custom/skills/reliable-web-app-operations/references/observability-and-incidents.md).

### Follow-up: active consumers and worker policy

Predeployment inspection caught an additive avatar field that the existing
consumer's strict schema would reject. It was not activated. The replacement under
test keeps the default response unchanged and exposes the field only through an
explicit opt-in. This catches a release-order and rollback problem that a new
owner/new consumer fixture alone would miss; verification of that replacement is
still pending this observation.

A worker preflight also stopped before process changes because a source template
omitted an explicit launch flag present in the running worker. The candidate
preparation now preserves the existing value, including false/empty, and rejects
conflicts. Eight controller tests passed; the live retry and normal scheduled
handover remain separate gates. The new legacy-launcher guard passed two local
tests but was not yet deployed at this observation.

Application evidence remains in the current migration record (revision `522ca0e`)
and ops handover record (`1a791b5`). These are bounded implementation/preflight
observations, not proof of full segregation or financial success. The generic
stage reference above now includes deployed-consumer/rollback contract checks and
actual-process policy preservation; subsequent app evidence should update these
pending outcomes rather than erase the failed approaches.

### Follow-up: completed worker fence and environment isolation

The opt-in response replacement subsequently passed the clean owner build and
live compatibility reads. During worker activation, the old scheduler stopped
correctly, but a repeated verification gate rejected an unsafe database role
before replacement configuration was installed. The same check passed when run
directly. Prisma's environment loading had contaminated the controller process;
Node's env-file option did not override the inherited database variable.

The replacement explicitly overlays the pinned worker environment in the child
process. A narrowly scoped stopped-state recovery revalidates old-process absence,
source/configuration/database pins, no replacement processes and fresh telemetry
before installation. Nine controller tests and an independent read-only review
passed. The VM recovery then completed both normal scheduled batch log/trace
correlations and boot enablement, with the old scheduler stopped. Subsequent local
Docker I/O errors initially prevented an independent process inspection. Removing
only reproducible inactive build artifacts and recovering Docker restored access;
the follow-up inspection confirmed both workers active. Later owner upgrades again
drained workers before selecting releases, then verified their normal log/trace
correlation. No external payment recovery or completed segregation is claimed.

A scheduled worker also returned a failure exit during an intentional, fully
drained stop because its last batch had failed. The replacement keeps batch failure
in telemetry/backoff and returns zero for a completed scheduled shutdown; one-shot
execution still returns nonzero for failed work. Real child-process signal tests
cover backoff cancellation and in-flight drain. Use this distinction when a service
manager otherwise misclassifies an operator stop as a process crash; do not suppress
actual one-shot failures or unfinished drains.

Reuse explicit subprocess environment ownership when orchestrating multiple
owners or importing clients with environment side effects. Preserve a safe
diagnostic code and executable/exit category without dumping arguments, raw
stderr or credentials. A post-stop failure needs a checked recovery path, not a
blind rerun of the initial drain or revival of an older scheduler. Current app
evidence: `servinoza-ops/docs/WORKER_HANDOVER_REVIEW.md` revision `872a82a` and
`servinoza-docs/MIGRATION_EXECUTION.md` revision `36f1f60`, 28 September 2026.

A later history-reader preflight found that the new service and compatibility
application wrote separate audit files, with older attempts in retained rotations.
Reading only the new service's file would silently lose earlier failures. The
source replacement merges the two bounded streams by operation identity before
existing relay correlation and retains partial acceptance and unreadable-source
warnings. Synthetic fixtures passed. The later ordinary-process handover preserved
the single journal writer and existing provider settings; narrow runtime log ACLs
and the service-user history parser passed against retained files, as did ordinary
user denial. Rotation configuration passed a full dry run after correcting an
older overlapping wildcard stanza; actual scheduled rotation and the fresh admin
browser journey remain unverified. Reuse the writer-path and continuity inspection
before moving any operational-history reader, rather than inferring completeness
from an HTTP success or zero rows.

Independent review rejected three initial handover-tooling assumptions: testing
before dependency pruning did not test the shipped closure; privileged copying
from build-user-writable paths left a race after validation; and a completion-record
failure could roll back an already healthy process. The replacement quiesces a
bounded build process group, emits a no-follow snapshot under the build identity,
then tests the final protected, pruned runtime with synthetic transport and
restart/replay. It consumes handover attempts before stopping a service and treats
post-success bookkeeping failure as record repair, without switching the runtime
again. Race/recovery fixtures, independent source review and the actual VM build
passed for this new helper. Older build helpers were outside that review; do not
generalize its result to every deployment path. Evidence: operations `534d414`.

### Follow-up: page success hid a missing mutation route

**2026-09-28 redirect follow-up:** A later extracted administrator frontend passed
signed-in navigation and a readiness check that inspected only the redirect path.
Anonymous public visits failed because middleware constructed its redirect from a
framework URL containing the private listener hostname and port. Correct forwarded
host headers alone did not change that framework URL. A compiled HTTP regression
reproduced the failure against the previous artifact. The correction uses the
configured public origin, tests the entire Location value with untrusted forwarded
headers, and adds that check to the build and handover path. The initial observation
had unit/type/build evidence with public activation pending. A subsequent 28 September
handover selected the corrected frontend: four anonymous public redirects retained
the configured origin and their login targets returned 200; a real browser also
followed the corrected entry path. The installed 23-case public site check passed
again after the compatibility process and its saved autostart entries were removed.
This establishes that bounded runtime/public-path result, not every authenticated
mutation or provider transaction. Reuse full-origin assertions and actually follow anonymous
redirects alongside signed-in checks; a path-only assertion or successful protected
page does not prove the login entry path works. Detailed release evidence remains
in the application's migration record.

An extracted profile page passed clean builds, read checks and browser fixtures,
but its first real save returned 404. The old page had used a server action; the
new browser POST had no explicit public gateway binding. A fixture forwarded it
directly to its owner and concealed the missing hop. The page binding was rolled
back, and fresh readback proved that the test account's original value was intact.

The replacement adds an exact bounded POST route, preserves issuer cookies and
original origin headers, disables automatic mutation retries, and refuses page
activation until that binding exists. A real gateway regression first reproduced
the 404, then verified API-before-page ordering and existing limits. Public denial
checks and the actual authorized UI edit, persisted reload, restoration and second
reload passed, with protected fields unchanged and desktop/mobile views inspected.
Use this gate whenever frontend extraction converts server actions into browser
HTTP calls; a successful page GET and a direct-owner mock are insufficient.
Evidence: gateway `94d6540` and application migration record `36f1f60`.

### Follow-up: document shells and delayed reactivation

During payment-document extraction, independent review caught private review notes
leaking into print output. Suppressing the surrounding shell fixed that, but also
hid the only QA marker on an unpaid record. The replacement retains the explicit
test-account notice and financial warnings while hiding unrelated navigation and
notes. Production-browser fixtures exercised ordinary, held and unpaid QA records;
public read-only checks then compared both actors' financial text with a baseline,
inspected mobile/desktop rendering and generated labelled PDFs. No payment was
made. Reuse separate print/export checks when moving a document between shells;
a clean screen screenshot does not establish a safe shared document.

A separate classification-boundary review reproduced a delayed cancellation race:
work became terminal, its participant converted to a testing account, and later
settlement reopened the historical real-work record. Existing creation and active
work checks did not cover that status-only transition. The replacement serializes
the supported conversion and reopening paths on participant rows, preserves the
historical classification, and rejects mismatches inside the original transaction.
Restricted PostgreSQL tests exercised both lock orders, raw/ORM updates and rollback;
independent source review and deployed function-body/ACL/ledger checks passed.
No real cancellation or account conversion was used as a production test. The
guarantee does not cover arbitrary privileged classification edits. Reuse this
inspection for delayed settlement, retries and reactivation after account-state
changes. Original evidence stays in application migration documentation and owner
tests (Payments `d58cd3d`, canonical migration `7e98cba`, Web `6117d21`, 28 September
2026); these are bounded corrections, not completed service/data isolation.

### 28 September 2026 follow-up: release identity and acceptance scope

A repository's latest commit can contain only documentation while a prepared
runtime correctly identifies an earlier commit. Compare the complete declared
build inputs, retain the exact runtime source/archive identity, and record the
documentation revision separately. Do not rebuild an unchanged application just
to make those labels equal, or relabel old runtime bytes as newly built source.

Anonymous denial checks must follow the actual handler contract: an intentional
403 is not a regression merely because a generic policy summary predicts 401.
Neither response proves that an authorized user can complete the operation.
Probe the temporary listener actually launched for a candidate and follow the
links rendered by the public sidebar; guessed ports, stale selectors and direct
owner requests can test a different route from the user's journey.

Operational independence also includes credentials and process scope. Move
deployment-only credentials into an explicitly selected, protected operations
file before retiring the application checkout that previously supplied them.
Validate ownership, permissions and the intended database identity without
printing values. Quiesce the specific build process group and its descendants;
unrelated authorized builds sharing a Unix identity are not evidence that this
artifact's builder failed to drain and must not be stopped by a broad UID check.

Evidence at this observation: reviewed operations source `7738387`, Gateway
source `8335373`, committed documentation/runtime comparisons, local routing
fixtures and bounded ordinary-process handovers. Several domain owners were
activated, while the administrative frontend and final Gateway selection were
still pending. Authenticated acceptance, final retirement and later delivery
stages were not established. Detailed release records remain application-owned;
this addition is a reusable decision record, not a completed-migration claim.

### 28 September 2026 follow-up: deleting a retired parent checkout

Stopping a compatibility process did not remove every dependency on its checkout.
A log collector still mounted the old log folder, and a healthy database container's
Compose labels still named its original deployment directory. The latter did not
affect current queries, but would leave an operator without the recorded recreate
path after deletion. Audit both runtime references and recovery configuration;
absence of active processes alone is insufficient.

Move historical logs into protected state storage, preserve the collector's image
and positions volume, and verify fresh ingestion after the mount change. Preserve
a database recovery configuration with an explicit existing external volume and
required credential; compare its resolved metadata with the running container
without printing credentials or restarting the database. Treat an omitted OCI
user and Docker's empty default consistently, while rejecting actual user drift.

Make the parent path unavailable reversibly before deleting its source. In this
case, real customer/partner browser and authenticated read journeys, site checks,
and a bounded API admission sweep passed with that path absent. Those checks do
not prove real provider money movement or every delayed job. Retain operator
configuration and evidence separately from obsolete code, and record the exact
deletion scope and remaining infrastructure separately. Application-owned
`MIGRATION_EXECUTION.md` and DB-ops runtime verification hold the original evidence;
this entry records the reusable method, not a claim that every cleanup step passed.

An operator subsequently required every owner repository to be visibly cloned on
the VM and all remaining infrastructure removed from the earlier parent tree.
Artifact-only deployment had satisfied application runtime independence, but did
not satisfy that explicit checkout and infrastructure requirement. State these
separately before declaring completion. A documentation repo and a UI package are
not extra daemons; show how each actual checkout supplies source, tooling,
configuration, dependencies or operator documentation.

For this correction, source archives reproduced from all seven owner checkouts
matched the selected release hashes, and rebuilding the UI package from its owner
source reproduced every consumed package file. Those proofs avoided unnecessary
application rebuilds while establishing lineage. Remaining infrastructure needed
its own transfer: a reload cannot move an old master process's working directory,
arguments or open files, and changing a Docker bind source requires recreating the
affected container. Preserve private runtime configuration and durable volumes
outside Git, use the owning repo for reproducible tools/configuration, and verify
public traffic during the handover. Record final cleanup separately; source
lineage alone does not prove the operational transfer completed.

### Follow-up correction: honor the operator's filesystem boundary

On 28 September 2026, the operator explicitly rejected separate host directories
for releases, QA, configuration and database tooling, even after the old parent
was removed. A conventional source/config/state split was technically workable
but did not satisfy that requirement. Do not defend a conventional layout as if
it supersedes an explicit placement constraint. Define an observable acceptance
check for the requested directories before another move.

The replacement puts each component's generated runtime and private files beneath
its owner checkout, excluded from Git and protected by filesystem permissions.
This is not a rule to commit credentials or relocate standard operating-system
storage. Document the distinction between project directories and OS registration
files, binaries, certificate stores or engine-managed volumes. Preserve existing
data and configuration values while changing paths. Update the release tools too,
so the next deployment cannot recreate the rejected layout.

Concrete checks from this correction: inspect ancestor traversal as the actual
service user; rebase absolute cache symlinks and QA manifests; preflight log owners
before stopping Nginx; handle a partially stopped worker/API pair during recovery;
compare Docker mounts by destination rather than unstable inspection-array order.
Repository presence, clean Git status and a successful health response are each
insufficient alone. Original execution evidence and final completion status remain
with the application's migration document; this entry captures the corrected
method, not a financial-transaction or backup-restore certification.

### Applying extraction lessons without repeating the extraction

A 28 September 2026 follow-up adopted narrowly verifiable parts of newer central
discussions into an already separated application. A read-only database command
checks explicit allow/deny permissions using the saved service login. Real
disposable PostgreSQL testing reproduced missing access to a newly added column,
then passed after its scoped grant; PUBLIC/inherited leaks and elevated membership
failed. The first integration run caught a schema-name quoting error that unit
doubles had missed. Backup/restore fixture success remains separate from production
scheduling, off-host recovery and a completed physical database split.

Actual npm-packed UI artifacts were installed in two isolated synthetic consumers.
Packing a candidate left both unchanged; upgrading one and reinstalling its prior
manifest/lock left the other unchanged. This establishes package-consumption
isolation, not deployed frontend/image rollback. No frontend source merge was
needed to test that property.

The existing private documentation reader was extended to publish current records
beside immutable historical imports, with local diagram rendering and explicit
source-baseline/digest identities. Independent review found that removed catalogue
coverage could retain old evidence; reconciliation now rejects that disappearance.
Browser checks exercised diagrams, navigation and mobile layout; unresolved source
references remain visible instead of silently linking a moving branch.

Reuse: turn a case lesson into an executable check of the target's actual boundary,
preserve the chosen delivery stage, and distinguish package, database, browser and
provider evidence. Do not infer that a repo merge, new infrastructure or live data
cutover is needed merely because another project proposed it. Provenance and
commands are retained in the application's Docs `ARCHITECTURE_ADOPTION.md`, DB-ops
`runbooks/VERIFICATION.md` and Design System README; this central entry records
local uncommitted implementation/testing, not publication or production activation.

A subsequent source-boundary review corrected an overly broad "no new repository"
answer that had considered only the shared component library. A visual package
owner and the application source owner solve different problems. Review the whole
target map before giving a count: source consolidation may remove owners while
a genuine domain extraction adds another, leaving the number unchanged. Ground a
new domain in actual commands, state and restricted data ownership; preserve shared
financial locks during staged extraction. Distinguish that evidence from speculative
future products, unknown team size and unmeasured scaling benefits. The application
adoption record preserves the specific recommendations and source references;
this follow-up is a reviewed proposal, not another deployed migration.

### Physical storage and frontend artifact checks

A same-day implementation follow-up made an explicit separate-container requirement
observable: distinct PostgreSQL cluster identifiers, data mounts and credentials,
plus actual wrong-domain credential rejection. Preserve the source database's major
version during extraction; do not silently combine isolation with an upgrade.
Synthetic multi-container bootstrap checks remain separate from application schema
migration, shared-lock replacement and authority cutover. A staging target is not a
completed isolated service merely because it accepts a restricted login.

Provisioning must also recover from a committed bootstrap whose response was lost.
Use the recorded container identity and durable transaction marker to verify the
outcome before retrying. Never recreate a database to resolve an uncertain commit.
When initialization did not commit, prove the target is still the expected empty
initial state before applying bootstrap SQL. Keep foreign or unexpected state intact.
Owner provenance: DB-ops `scripts/domain_containers.py` and
`runbooks/DOMAIN_CONTAINERS.md`, source revision `3bf12ca` on 28 September 2026.
Actual disposable-cluster tests passed; production authority was not moved.
Review also caught a fixed pending-receipt filename blocking recovery after a
process crash. Unique same-directory atomic temporary files preserve unknown
orphans without blocking later writes; focused tests verify old-receipt preservation.

Independent frontend review found another reusable release trap: framework
standalone output can contain loaded `.env` files. Copying the directory wholesale
can package server credentials even when source-control ignore rules are correct.
The replacement assembler excludes dotenv files from runtime/static/public output;
a synthetic-file regression verifies exclusion while preserving required assets and
the original inputs. Inspect the artifact itself, not only Git status. This does
not make deliberately public build-time values private or prove a complete secret
scan. Owner provenance: Frontend `scripts/assemble-app.mjs` and its packaging test,
source revision `46d851d` on 28 September 2026; no production secret leak was
observed or claimed. Source publication is distinct from deployment approval:
an intermittent full-browser hydration failure remained a release gate despite
passing builds and narrower suites. Unproven runtime fixes were reverted and the
reproduction retained; a fixture failure was not reported as a proven live outage.

### Follow-up: verify the runtime boundary and the actual renderer

The first active database cutover moved one complete owner, rather than switching
all prepared containers at once. Its foreign account lookup became a narrowly
scoped owner API with fail-closed behavior. Native typed transfer compared schema,
nullability and PostgreSQL data digests under a writer fence; the retired SQL login
was disabled. The running process's connection, restricted-role queries and a
restore into an independent container were checked. The source partitions happened
to be empty, so this is not evidence of a populated production transfer; separate
synthetic tests exercised typed values. A local unencrypted recovery archive also
does not establish encrypted, recurring or off-host backup readiness. Reuse the
separation between a provisioned target, a tested candidate and an active authority.
App provenance: Engagement `e73912e`, DB-ops `b3c64ac`, Ops `a57425e`, and Docs
`DATABASE_SEPARATION.md`, 28 September 2026. Original receipts stay with the app.

The frontend gate was later recovered through a concrete upstream failure mechanism.
Production diagnostics expected a host element while React's hydration cursor was
already at its child. Checking the renderer bundled by the framework—not just the
top-level React package—found the missing host-replay cursor restoration from
[React #35494](https://github.com/react/react/pull/35494). A delayed lazy-route chunk
regression failed on the unchanged build. A keyed Fragment moved reconciliation
onto a non-host fiber without changing HTML, disabling SSR or suppressing errors.
The same reproduction and full browser suite passed afterward. Earlier title-effect,
transition and Suspense guesses remained recorded as failed attempts. This is a
version-specific workaround, not a rule to wrap every component; reevaluate after
a framework upgrade that contains the upstream fix.

A separate browser-test failure waited for the home URL after signing out while
already on that URL. Cookie removal preceded the actual navigation, so the next
page navigation raced logout. Registering the navigation observer before clicking,
then checking anonymous UI and cookies, exercised the real completed flow without
changing logout behavior or adding a fixed sleep. Frontend source `f7a9425`, its
`VERIFICATION.md` and ignored browser evidence preserve the failing and passing
runs. Full synthetic-owner browser checks passed; production selection, real
identity-provider callbacks and real financial transactions were not established.

A subsequent owner cutover verified a populated synthetic user journey through
the real public route and real account/fee-policy dependencies. Test accounts
created owner data, exercised stale-state and wrong-actor rejection, and were
denied real financial obligations. Count the resulting writes in the new cluster
and prove the fenced source stayed empty; a successful HTTP response alone does
not show which database owns the operation. The independent restore compared
snapshot-consistent data digests and runtime grants. Its first clean restore
failed because the provisioned extension depended on the existing public schema;
the corrected restore reused that verified-empty schema rather than dropping the
extension or weakening restore error handling. Adapt archive selection to the
actual provisioned target and preserve the failed attempt's evidence. App source:
Docs `DATABASE_SEPARATION.md` at `a508fdb`, 28 September 2026. This proved that
owner's QA workflow and same-host recovery; it did not prove other domains were
isolated, real payments worked, or off-host backup was configured.

Frontend consolidation then passed ordinary VM builds, real customer/partner
sessions, a real administrator identity-provider callback and persisted QA-run
history. Relocating only the process cwd was insufficient: a final inspection
found diagnostic credential-file environment paths still pointing into the old
owners. The fix copied scoped credentials with their original permissions and
switched only those runtime paths through a temporary listener. Retirement checks
covered cwd, open files, environment path references, units, active configuration
and the QA manifest, followed by a reversible directory removal and real public
journeys. Admin history relocation briefly fenced new QA commands and drained
existing jobs. Review caught that unfreezing writes before fallible cleanup could
trigger an unsafe rollback; commit the handover first, then treat an uncertain
final route reload as reconciliation. Provenance: Ops `1839442`, `ec9f0b1`,
`1970e01` and Frontend `VERIFICATION.md`, 28 September 2026. Source snapshots used
by an administrative QA runner can lag live releases; reporting a passing run must
retain those revision limits rather than treating it as a current whole-app gate.

On 29 September the operator explicitly made beta data disposable. Adapt the
plan immediately: remove historical backfills and compatibility as acceptance
requirements, while retaining owner isolation, authentication and financial
invariants. A minimal reset seed should whitelist only necessary administrator
identity mappings and synthetic test accounts, revoke copied sessions, omit
provider tokens and refuse a nonempty destination. Here an initial seed failed
on a restricted legacy profile read. Generating fresh synthetic profiles removed
that dependency; widening the old runtime's SQL privileges was unnecessary.
The retry committed the minimal seed on a separate owner cluster. App provenance:
Accounts `61c51d1`, `scripts/seed-clean-beta.mjs`, and owner
`DATABASE_SEPARATION.md`. This establishes seed behavior only; creating separate
containers and passing builds does not establish a complete traffic cutover.

The subsequent clean-owner cutover passed public customer/partner password login,
administrator identity-provider login, request creation/acceptance, account and
booking pages, and a cross-owner issue hold. An independent runtime checker
verified six distinct database containers, cluster identities, storage paths and
restricted owner logins. Process environments covered APIs and workers; the old
database had no client sessions before removal. These are bounded runtime and QA
results, not real provider payment or payout evidence. App provenance: Ops
`5222519`, DB-ops `6aa2c6e`, Accounts `5fbdb25`, Verification `b9434e8`, Bookings
`72d9d11`, Payments `bc8f3e1`, and the app's `DATABASE_SEPARATION.md`.

Three additional acceptance rules came from this completion:

- A clean database baseline must include handwritten constraints, partial unique
  indexes and immutable-record rules from migration history. ORM schema generation
  alone omitted financial protections. Exercise deliberately invalid writes
  against the actual clean baseline before selecting it.
- Test the actual owner HTTP servers together. Unit-shaped adapters missed a
  cancellation release race: an older resolution could clear a newer issue.
  Pin assignment and issue identity, preserve idempotency receipts, and test
  delayed/replayed releases against the new state. The final regression used
  separate disposable databases and real owner sessions; arrival was an explicit
  fixture prerequisite and provider money movement was not exercised.
- Public and server-only contracts have different routing. A diagnostic initially
  called an internal page-data endpoint through the public gateway and received
  404. Check the declared route before treating that as an outage or exposing a
  new public endpoint. Exercise the real rendered page and its owner call instead.

## Container handover preparation, 29 September 2026

The next stage used local multi-platform builds and public registry publication,
keeping automated CI/CD deferred. The Panyora case's central build contract was
adapted to service-owned manifests and platform-owned recipes, with separate app
version/source revision and immutable image digest evidence.

Two failed assumptions were caught before traffic selection. Desktop Linux disk
space exhausted even though the Mac filesystem still had capacity; exact completed
task BuildKit records were removed and final-image checks retried. A readiness
probe inferred all owner SQL usernames from one convention; inspection found two
legitimate different roles. An explicit identity map and executable positive and
negative probe tests replaced the assumption. Hung probes now have deadlines that
reach rollback rather than waiting indefinitely.

Runtime inspection also required preserving compiled public frontend settings,
pinning committed platform recipes despite unrelated local edits, and changing
log collection from systemd unit selectors to exact Docker journal tags. Actual
read-only frontend image tests exercised HTTP readiness, dependency failure and
native image processing. These preparation results are not traffic-cutover proof.
Original receipts and deployment outcomes remain in the app's own documentation.

Provenance: Ops `fb8294a`, `70dcaca`, `83a0374`; Frontend `52d16a0`;
`scripts/local-images.mjs`, `scripts/container-runtime.py`, and the app's migration
execution documentation. Reuse the handover checks in
[central container builds](../../custom/skills/reliable-web-app-operations/references/central-container-builds.md).

The subsequent traffic handover passed public customer/partner login and a
synthetic booking/issue workflow. An administrator's real QA action then exposed
an omitted OS identity: the preserved host UID did not exist in the distroless
passwd file, and a deliberately scrubbed child environment had no `HOME` fallback.
A read-only per-container identity mapping fixed native home lookup without
widening the child environment. The same UI Prisma-validation and site-smoke
actions then passed. These QA commands use explicitly pinned source snapshots,
so they establish runner compatibility, not complete current-source coverage.

Retirement inspection also found that disabling linked systemd units removed
their definitions. Capturing the canonical definition/hash and relinking without
enabling or starting preserved the rollback entry point. The regression models
that unlink behavior and rejects changed definitions. Provenance: Ops `26418fc`
and `d5dac72`; original public-flow and run evidence stays with the app. No real
provider payment or payout was performed by this container acceptance work.

### Source retirement and CI handover follow-up, 29 September 2026

Image packaging alone did not make application checkouts disposable: containers
still bound owner-local secrets and state, the proxy used certificates/logs/static
assets there, and the collector mounted those logs. A two-stage relocation copied
only required runtime paths, stopped writers for the final copy, verified the new
paths, then checked container mounts, process references and active unit definitions
before deleting the retired checkouts. Proxy recovery uses its preserved operational
plan even when both the source checkout and collector container are absent. Unit
tests cover that recovery boundary; actual proxy/app health and signed-in reads
passed after relocation. Private evidence remains with the application.

The replacement release workflow separates hosted source builds, archive validation
and publication, and an unprivileged deployment runner. Its root-owned deployment
helper accepts bounded non-symlink receipts, preserves unselected images/settings,
and restores previous images on failure without rolling back database data. Source
retirement is a prerequisite to this deployment path. Freeze all source revisions
before matrix fan-out, particularly when two images share a repository.

Runner registration exposed an additional assumption: the runner's .NET host
required listing access to every parent directory, not merely traversal. Scoped
read/traverse ACLs on the restricted ancestors replaced a proposed broad permission
change; private child directories and secret file modes remained unchanged. This
is a registration compatibility fix, not justification for granting Docker or
repository write access to the deployment identity. After registration, placing
the runner inside an ES-module repository also made its upstream CommonJS service
entrypoint fail. A runner-local `package.json` with `type: commonjs` restored the
upstream module contract; a real Node test reproduced failure before and success
after. The dedicated runner then connected with its narrow deployment privilege.

Status at capture: runtime relocation and ten-checkout retirement observed; local
receipt/rollback tests passed. Hosted build, publication and deployment acceptance
were still pending at that checkpoint and could not be inferred from these checks. Provenance: Ops
`a6d677e`, `df4c6f8`, `b875812`, `0224631`; owner release documentation records the
subsequent workflow outcome. Reuse this sequence when removing build-time source
from a stateful host, and verify the target's actual bindings and public workflows.

Independent release review then found two acceptance defects before final
promotion: public checks originally ran after the helper had declared success,
and an anonymous-admin probe named a nonexistent route. Moving public checks into
the image-rollback boundary and selecting an actual protected route retained an
exact denial assertion. Actual public checks passed after correction; the local
failure regression verifies image rollback without database commands. Workflow
revisions are immutable within a running Actions run: a correction to main cannot
repair that run's final steps. Preserve its built/scanned artifacts and promote
their exact digests through the corrected workflow rather than overwrite tags or
report the first run as successful. Provenance: Ops `794b8e4`, `d86c6c1`, `c5e4686`;
the final promotion outcome still belongs in the owner release evidence.

The follow-up completed eight hosted builds and separate scan/publication jobs.
The original workflow was cancelled before its deployment job ran; the corrected
workflow promoted the same eight digests successfully. Independent checks then
matched all ten running processes to the new image/source identities, with the
same six database containers and only the two retained operations checkouts.
Signed-in customer/partner reads, a synthetic booking/issue flow, QA-payment denial,
and the administrator's pinned-source validation/site-smoke actions passed.
This is bounded runtime and workflow evidence, not proof of real provider payment,
mail delivery, all business cases or a new disaster-recovery drill. Owner evidence
and exact run identifiers remain in application release docs; baseline Ops
`d6a086a` records the published image selection. The target-specific lesson is to
verify actual workflow revisions and reuse verified artifacts after orchestration
corrections, without rewriting immutable image tags or hiding a cancelled run.

### Automatic versioning correction, 29 September 2026

The container handover used changing source suffixes with an unchanged package
version. That proved image identity, but missed the requested automatic version
updates despite the central build guide linking the release-versioning reference.
The correction adopts pinned Release Please with independent component versions,
real deployed bootstrap commits and separate frontend component tags. Version PRs
update package versions, lockfiles and changelogs; image selection checks a stable
published tag against its exact source and committed package versions. Retries and
digest promotions retain their existing version.

Actual-library tests cover first/subsequent increments, no-op commits, component
isolation, shared frontend inputs and missing history. A real read-only provider
preview returned no pending releases for all eight deployed components. Dedicated
cross-repository write access is still pending, so automated PR/tag publication
must not be claimed verified. Source: owner Ops `scripts/app-versions.mjs`,
`scripts/release-sources.mjs`, `config/app-versions.json` and `docs/container-ci.md`
(reviewed working changes at capture; original evidence stays with the app).
Reuse the linked versioning reference before declaring container CI complete;
verify version calculation and publication separately from image/deploy success.

### Worker ordering and maintenance follow-up, 29 September 2026

Review of the image rollback path found that starting API and worker containers
together could resume work before public acceptance. Recovery also needed to
verify the restored public path before recording success. The replacement pauses
selected workers, starts and checks selected APIs plus the public path, and only
then resumes workers. If final recovery readiness fails, selected workers are
stopped again and the receipt reports recovery required. Unselected services and
database data stay outside the rollback mutation scope.

A disposable local Compose rehearsal used real cached images/container lifecycle
and the deployment algorithm with synthetic HTTP, database-probe and provenance
adapters. Candidate direct health passed while its login failed; previous-image
recovery passed, two accepted writes and eight unselected container identities
survived, and worker order was asserted. The final rehearsal passed; its isolated
resources were removed. This does not establish a production rollback or financial
workflow recovery. Original evidence remains with the application. Reuse the
ordering rule for stateful workers and test the public failure/recovery path, not
just process readiness or mocked command order.

The maintenance release implementation separately validates an explicitly approved
deployed baseline, ancestry, patch-only increments and a forward-port issue. It
prevents maintenance publication from becoming GitHub's latest release or shadowing
main's release selection. Tests use the pinned release library and actual SDK
transport; a real read-only main preview passed. No maintenance release was created
and cross-repository write activation remains pending a dedicated credential.
Provenance: owner Ops `scripts/container-upgrade.py`,
`test/test_container_rollback_drill.py`, `scripts/release-tracks.mjs` and
`docs/hotfixes.md`, committed in Ops `41549e5` on this date. Hosted contract tests
subsequently passed and the helper was installed with matching hashes and unchanged
running containers. Detailed release and installation evidence belongs in the
owner's Docs `MIGRATION_EXECUTION.md` and Ops `docs/container-ci.md`.

### Local parent retirement, 29 September 2026

After container/CI handover, the obsolete local monolith still surrounded the
independent repositories. Cleanup first checked live process/mount ownership,
local access-container mounts, repo working changes and client paths. Unique
parent changes, Git metadata and release evidence were hashed into an ignored
private owner archive before removing caches and the runnable parent tree. Repo
HEADs and staged/unstaged diffs were compared across the move; the resulting
workspace contains only direct repository directories. Standalone documentation
and release-tool checks passed from the new paths.

Two limits matter when reusing this sequence: an old inventory generator that
requires the monolith is a historical collector, not current owner-only tooling;
and a global MCP command may point at a deleted local wrapper even though the
production service is independent. Retarget such client paths within explicit
authorization and report pending edits. Do not declare the entire host
container-only when ingress, SMTP or runners remain host services. Original
archive and relocation evidence stay with the owner Docs migration record.

### Strict internal contracts and live schema capability, 2 October 2026

An authenticated administrative page remained broken through several individually
reasonable repairs. A consumer first lagged a producer's strict response schema.
After that compatibility update, the deployed application expected a database
function overload that its live owner database had not received. Applying the
additive migration exposed a third defect: the producer selected a password hash
to calculate an authorization flag and accidentally spread the hash into its
internal response. A strict downstream schema rejected the unexpected field and
the UI surfaced the dependency failure as a generic server error.

The replacement keeps credential material inside its owning service, derives the
authorization flag locally, and returns an explicit credential-free projection.
The regression first failed on the presence of the hash, then passed while also
asserting the authorization flag remained true. Deployment verification separately
checked the running database capability, the live internal response keys, the
authenticated page after a stable reload, and a current screenshot. Unit tests,
image scanning, deployment success and anonymous canaries had not proved that
combined journey.

Reuse these gates when a release changes authentication or a cross-service read:

- Test exact producer output against the consumer's strict schema, including a
  negative assertion for credentials and private fields.
- Treat a selected secret as tainted even when it is needed only for a derived
  boolean; destructure it out before forming the response.
- Verify required database functions, columns and grants through the running
  application's actual connection before calling a deployment compatible.
- Exercise the authenticated public route after deployment and preserve failures
  encountered between partial repairs instead of replacing them with the final
  success claim.

Status: adopted and live-verified for the affected administrative read; no payment
or money movement was involved. Provenance: sanitized owner Accounts release
`da9dba0`, DB Ops migration revision `70fb4cf`, and application-owned release
evidence dated 2 October 2026. Exact identities, screenshots and runtime receipts
remain with the application.
