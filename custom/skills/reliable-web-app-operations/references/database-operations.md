# Database lifecycle, migrations and recovery

## Ownership before directory/repo choices

Give database operations a named owner even when no dedicated repo exists. A separate DB-ops repo can own provisioning/container configuration, backup/restore tooling, private configuration locations and operational checks. It need not own domain migrations or expose an HTTP endpoint.

Represent the database as a stateful runtime resource in architecture/deployment diagrams. A container name is an instance identifier, not a repository, service contract or migration plan. Document mount/data paths, configuration/secret owners, network/listener policy, backup destinations and recovery dependencies.

Keep live data, dumps and private credentials outside Git and application artifacts. Moving code directories must not accidentally move, reset or orphan database storage. Verify resolved mounts/paths and active connection configuration before migration or cleanup.

## Access and schema verification

- Separate administrator/migration credentials from runtime roles. Check actual grants and denied operations, including expected schema/table/sequence privileges and narrowly justified cross-domain reads.
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
