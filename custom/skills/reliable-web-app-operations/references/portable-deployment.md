# Portable deployment and immutable promotion

Use when a central release platform must support multiple deployment topologies.
Keep project names, cloud identifiers, secrets and exact topology in its runbook.

## Configuration and execution ownership

- Separate app runtime/build declarations from the ops-owned environment topology.
  A single deployment-kind enum avoids contradictory enablement flags. Implement
  each agreed backend; a validation branch that only reports “unsupported” is not
  backend support. Invalid configuration or unhealthy runtime must still fail.
- An ops adapter can run separate Compose projects on named private hosts;
  cross-host placement, networking, discovery and recovery require explicit
  orchestration. Kubernetes needs service discovery, replicas, Secret references,
  ingress, job and storage contracts.
  A mode selector does not provision infrastructure or migrate databases/DNS.
- Preserve an existing deployment path while adding adapters. Audit hardcoded
  loopback clients, host binding, TLS hostname verification, forwarded-IP trust,
  worker schedulers and database connections before declaring portability.
- Public hosted runners cannot reach arbitrary private addresses. Make runner
  placement/network access explicit. Keep deployment credentials scoped to a
  protected environment; service teams need no duplicated pipelines.

## Promote the artifact, not a rebuild

- Bind retained artifacts to provider repository identity, trusted workflow,
  successful run attempt, source SHA and artifact digest. Validate archive paths,
  sizes and contents without executing them. Never silently replace a missing
  artifact with a fresh build or a “latest” tag.
- Preserve original image-build tooling revisions separately from current
  deployment tooling revisions and environment hash. Deploy immutable digests.
- Verify registry object/config digests and image provenance on each backend,
  not only the legacy backend. Do not forward provider credentials to a signed
  artifact storage URL. Test a real retained provider artifact in addition to
  fabricated ZIP/HTTP fixtures.
- When extracting a reusable workflow, recheck context availability with a
  workflow linter and actual provider OIDC claims. Caller workflow identity and
  reusable job identity differ. Existing cloud trust may reject a new promotion
  caller even when its code and secrets are correct.

## Bind environment approval to an immutable candidate

Branch names describe a source lane; they are not release identities. For a
development → staging → UAT → production model, define the candidate carried
between environments as the pull-request number and exact head SHA plus the
complete source-SHA/artifact-digest set, deployment configuration identity and
reviewed migration set. In a multi-repository system, keep one release manifest
as the system-level compatibility record instead of treating independently
moving branches as one candidate.

Create an isolated synthetic development environment per active backend PR or
branch when local peers would expose unrelated source, credentials or schemas.
This can be a namespace or Compose project on shared infrastructure; it need not
be a VM per developer. Frontend-only work can use bounded local mocks and a
shared integration environment, reserving a per-PR environment for unreleased
backend integration. Make Staging the default remote backend for frontend
engineers after producer changes merge. Give frontend contributors only the
application URL, synthetic identities and scoped diagnostics they need; do not
grant database, container-host, VM or internal-service credentials. UAT access is
for controlled candidate verification and defect reproduction, not a mutable
development loop. Production access should use approved observability/support
paths and must not become routine customer-data browsing.

Use staging for continuously merged integration and UAT for one stable release
candidate. If the UAT PR head, any artifact digest, configuration hash or
migration set changes, dismiss previous approvals and rerun the required UAT
checks. Do not let a moving staging branch silently change the candidate under
QA. Production canary and full rollout must promote the UAT-tested digests
without rebuilding; record canary success, full promotion and rollback as
separate outcomes.

Document implementation status explicitly. A branch diagram or environment
name does not prove that per-PR provisioning, approval invalidation, artifact
promotion, data isolation or rollback automation exists. Verify the provider's
actual branch-protection and environment-gate behavior, then exercise a changed
PR SHA and confirm that stale approval cannot reach production.

## Transactions, jobs and recovery

- Acquire durable ownership before mutation; save original topology hash,
  complete participating host/service set, selected images and prior state.
  Recovery must verify the same transaction scope before claiming any host.
- Worker draining must cover pre-start work. A cron process can hold its lock
  before a container exists. Coordinate with that lock and a durable pause marker
  checked under the lock. Polling containers alone misses this race.
- A Kubernetes Job with absent/zero `status.active` can still be Pending and run
  later. Wait for explicit terminal conditions and account for nonterminal Pods.
  Discover scheduler Jobs by Job metadata and controller ownership, not just Pod
  labels. Do not replay financial or migration jobs automatically after timeout.
- Prove the original executor has stopped before recovery; claim ownership
  conditionally (resource version/token). Parent-process death alone may leave
  SSH or Helm children; reconcile the process group and remote ownership too.
- Restore all participating services before resuming the old scheduler. Retain
  locks after incomplete rollback. A failure in final bookkeeping after runtime
  verification should lead to record repair, not blind job replay.
- Recovery should not require the failed candidate to remain downloadable when
  recorded previous artifacts are already available. Preserve data; application
  rollback is not database restore.

## Evidence and cleanup

Run real manifest rendering, workflow lint, gateway transport tests and bounded
failure-path orchestration tests. Keep mocked command execution distinct from a
live multi-host/cluster deployment and real provider money movement. Test the
normal hosted inspection path before claiming hosted workflow activation.

Clean only owned runner checkouts/credentials and completed recovery records.
Protect active/previous images, ongoing jobs, volumes and unrelated applications.
Document infrastructure prerequisites and untested live cutovers explicitly.

## Keep the documentation usable

Maintain one ops-owned target contract with complete machine-readable examples.
Distinguish the app's build/runtime manifest, the ops topology manifest, the
generated image release record and the deployment outcome. They are different
authorities even when several are called “manifest”. Keep secrets as references.

When adding a backend or promotion path, update older entry points as well as
the new runbook: publisher guide, release lifecycle diagram, existing-host
runbook, central architecture and source catalogue. Label commands that bypass
the generic dispatcher as backend-specific. Preserve dated evidence as history;
do not present old VM tests as proof of a fleet or cluster rollout. Refresh source
hashes after owner commits, then validate links, drift and the documentation build.
