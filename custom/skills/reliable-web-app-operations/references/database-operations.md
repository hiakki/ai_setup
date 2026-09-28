# Database lifecycle, migrations and recovery

## Ownership before directory/repo choices

Give database operations a named owner even when no dedicated repo exists. A separate DB-ops repo can own provisioning/container configuration, backup/restore tooling, private configuration locations and operational checks. It need not own domain migrations or expose an HTTP endpoint.

Represent the database as a stateful runtime resource in architecture/deployment diagrams. A container name is an instance identifier, not a repository, service contract or migration plan. Document mount/data paths, configuration/secret owners, network/listener policy, backup destinations and recovery dependencies.

Keep live data, dumps and private credentials outside Git and application artifacts. Moving code directories must not accidentally move, reset or orphan database storage. Verify resolved mounts/paths and active connection configuration before migration or cleanup.

## Access and schema verification

- Separate administrator/migration credentials from runtime roles. Check actual grants and denied operations, including expected schema/table/sequence privileges and narrowly justified cross-domain reads.
- When adding a column consumed across domains, inspect explicit column grants as well as table/schema changes. A migration can succeed as administrator while the real service role still cannot read the new field. Add the narrow grant through a reviewed migration and exercise the query using that service's connection.
- Verify required columns, tables, constraints, indexes and migration checksums against the application's actual database connection. Migration history alone does not prove schema shape or environment identity.
- Repair drift with reviewed, appropriately additive migrations. Do not hide it by baselining history automatically, destructive synchronization or copying one service's full admin environment.
- Coordinate one authoritative ordering strategy and locks. Independent domain migration chains can be valid, but shared objects/dependencies need defined ordering and compatibility. Test old/new application compatibility during staged rollout.
- Budget connection pools across services and replicas. Repo separation does not remove shared database contention or establish horizontal scalability.

## Backup and disposable restore

A backup command exiting successfully is only one evidence level. Check archive readability/integrity and perform a restore rehearsal in an isolated target before claiming recoverability. Verify schema, important counts/constraints and representative application queries; ensure the rehearsal cannot connect background jobs or providers to live accounts.

Preserve roles, extensions, configuration and encryption-key requirements needed for recovery, using secure handling. A logical data dump may not contain every cluster-level prerequisite. Record backup time, environment, tool/database compatibility, retention/access policy, recovery objective and measured rehearsal result.

Protect backup scope/paths against traversal, symlink confusion and accidental overwrite. Use unique destinations and explicit target validation. Do not assume a backup stored only beside the primary survives host/storage loss; assess independent storage and access controls against the required recovery objective.

## Scheduled backup retention

Make cadence, retention count, destination and environment explicit configuration.
Publish a completed archive atomically only after successful creation and integrity
checks; failed or partial output must not replace the newest good backup. Rotate
only completed archives owned by this schedule after success, with locking to
prevent overlapping runs. Keep pre-release or incident recovery backups under
their own retention policy. Verify scheduler execution, permissions, timezone,
failure notification and a restore rehearsal; configuring a cron line alone is not
backup evidence. A simple existing scheduler and owned script can suffice without
introducing a separate running backup service.

## Restore and host migration

Separate backup, inspection, disposable restore and live restore commands. Live recovery needs explicit scope, expected data-loss window, writer/worker coordination, a safe stopping condition and post-restore reconciliation. A normal app rollback must not replace newer customer data with an older dump.

For a host migration, inventory database version/extensions, roles, schema/data, storage, networking, credentials and all consumers. Rehearse, validate the target, coordinate writes during final transfer, verify the actual new connection path and exercise application queries/journeys. Preserve the old system according to a deliberate recovery plan until cutover evidence justifies retirement.

Dry runs must not mutate data or implicitly start/stop services. Locks should prevent overlapping backup/restore/lifecycle operations where necessary and have a documented interaction with deployment locks. Never reset shared, customer or durable demo data to conceal a failure. Explicitly disposable test databases may be recreated through their documented lifecycle.

State exactly which recovery evidence exists: archive check, isolated restore, application verification, measured recovery time or actual failover. Do not label an untested runbook as disaster-recovery readiness.

## Exact data transport and independent reconciliation

Preserve both numeric precision and JSON types during migration. Parsing decimal
tokens as strings can preserve a scalar SQL numeric insert while corrupting
numbers nested inside JSON/JSONB. Parsing them as binary floats can round money or
stock quantities. Use a native database transport, or an exact decimal decoder
and encoder that emits numeric tokens. Include a nested high-precision decimal
regression; do not use `default=str` as a precision workaround.

An importer and verifier sharing the same faulty decoder can agree on corrupted
data. Check counts plus actual values/types, then add an independent database-side
comparison or row digest and a restore rehearsal. Preserve failed-run evidence;
only discard a staging target after proving its identity, unchanged contents and
absence of application writes. Never reset the live source to hide a failed test.

Keep staged backfills visibly separate from active writer authority. New database
containers, copied tables and successful restores do not remove shared locks,
cross-domain authorization functions or duplicated sensitive fields. Enumerate
these contracts, deny premature runtime access, and report application cutover as
unfinished until the real workflows and final writer handoff are verified.

Preserve identity-sequence options and allocation state, not just table rows or
`MAX(id)`. Deleted rows, rolled-back inserts and cached allocations can consume
identifiers beyond surviving rows. Sequence allocation is not an MVCC snapshot;
observe it after the data snapshot and repeat under the final writer fence. Test
nondefault increments/cache, descending sequences and never-called empty
sequences through real SQL, including the next generated value.

Make multi-target migration retries reconcile durable per-target receipts before
advancing. A committed target followed by a lost response is not an empty target
to recreate. Bind source, schema, run and expected transform identities; verify
actual normalized and retained rows, access restrictions and unexpected objects.
Preserve attempt-specific phase journals, including the uncertain-commit phase;
do not overwrite earlier evidence or let a reused report filename mask failure.
Similarly, a running container does not prove initialization committed: verify
extensions, role restrictions, public revocations and saved-credential login on
provisioning retries before reporting success.

## Independent-domain cutover rehearsals and compatibility

Treat the source schema and actual runtime configuration as migration inputs.
A development snapshot can contain unreleased features that the running source
does not have. Rehearse both supported source shapes; reject partial/unknown
shapes instead of silently baselining them. A schema migration must not fabricate
business approval or silently revoke earlier publication. If a compatibility
bridge is necessary, bind it to verified source IDs and revisions, make it
read-only to runtime callers, define its retirement trigger, and keep new writes
on the current policy. Unknown historical facts remain unknown.

- PostgreSQL roles are cluster-wide. A fresh database does not make a reused
  login fresh: memberships from another test can invalidate default-deny staging.
  Use rehearsal-specific logins with no initial memberships, then grant only the
  verified domain capability. Preserve unrelated roles/databases. Login settings
  such as identity's search path must be configured on the actual login; group
  membership alone does not inherit role configuration. Readiness should check
  the intended principal/capabilities, database and actual privileges rather than
  accepting a familiar name or rejecting an otherwise valid isolated login.
- Keep durable equality-index and idempotency-fingerprint keys separate from
  rotatable inter-service bearer credentials. Require explicit purpose keys and
  test that bearer rotation leaves persisted hashes unchanged. A durable-key
  rotation needs its own verified reindex/reconciliation plan; do not silently
  fall back to the current service token. Existing rehearsals need the old logical
  hash key retained while changing its configuration ownership.
- Parse private environment files with the runtime's real dotenv semantics.
  Quote delimiters, comments and encoding can change signing/encryption keys.
  Compare logical values privately without printing them; configured files and
  actual process environments are separate evidence. Development dotenv fallback
  can inject old authority credentials into an otherwise scoped test environment;
  use an isolated artifact or explicitly prevent undeclared fallback values.
- Verify immutable source snapshots and original operational rows before writing
  opaque references or purging sensitive copies. Preserve differing historical
  notes as independent evidence instead of assuming equality. Retry only from the
  original or exact intended state. A multi-database interruption may leave an
  unused immutable snapshot, but must not remove the sole original value first.
- Prefer offline, source-bound financial/reference backfills before application
  writers start. Do not make a final migration depend on a cyclic set of live
  services or allow test-generated rows to be ignored during exact reconciliation.
  Keep irreversible provider actions and historical event publication disabled.
- Review OS lock ownership across the actual CLI-to-helper call chain. A second
  descriptor acquiring the same exclusive `flock` is not a reentrant nested lock.
  Keep import/preflight checks under the import locks, release them before a
  normalizer that owns its own lock, and revalidate immutable source/receipts after
  the handoff. Preserve the outer deployment/writer fence. A regression must use
  actual OS locks through the CLI boundary; mocked successful lock calls can hide
  a release-stopping self-conflict. Resume from verified durable receipts without
  dropping targets or weakening exclusion.
- Distinguish existing-password login, imported-session validation and a new
  synthetic-account login. If a local fixture's credentials differ from the actual
  source, investigate the mismatch; do not reset the source password or claim
  original login success from a reconstructed test cookie. Preserve those limits
  alongside the successful invoice/catalogue/data comparisons.
- Verify the active UI source and deployment manifest. Passing a retired frontend
  repository's build does not validate the deployed consumer. Migrate only the
  intended feature delta and retest the actual app.
- Verify the running gateway's upstream mapping against the current backend and
  frontend listeners after a local cutover. A preserved gateway can serve its
  normal port while retaining destinations from an older test. Owner health and
  direct-origin success do not prove the user-facing route. Inspect actual launch
  configuration, report intentional corrections, restart only within authorization
  and repeat the failing onboarding/page flow through the gateway.
- Separate reproducible package contents from compression-toolchain identity.
  If an exact compressed-archive test passes locally but fails on the image build
  platform, compare decompressed bytes and archive metadata before changing the
  source or replacing published packages. Identical tar bytes can have different
  gzip encodings across Node/zlib versions. Pin the uncompressed tar hash for the
  cross-toolchain content regression, retain same-toolchain repeatability checks,
  and keep published consumer archive integrity hashes and image digest checks
  exact. Never treat this distinction as permission to accept modified content,
  retag an immutable artifact, skip verification or claim a failed build deployed.

These rules originated in local source-specific rehearsals. The later
[reviewed live handoff](../../../../docs/case-studies/panyora-service-extraction.md#final-28-september-checkpoint-bounded-public-acceptance)
added actual owner-image migration, restricted access, isolated restore, public
workflow and scheduler/source-retirement evidence; it did not certify live provider
transactions or every recovery race. A new target still needs its own fenced
fresh source, checked owner artifacts/history, observed runtime destinations,
real public workflows and explicit recovery path. Another project's pass is not
inherited proof.
