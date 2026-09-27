# Multi-service release and legacy retirement

Apply only the parts relevant to the requested change. This reference adds multi-repository mechanics to the environment and release-evidence rules in `deployment-contract.md`; it does not grant deployment or deletion permission.

## Explicit runtime ownership

Assign owners for release artifacts/current selection, process definitions, configuration, ports, logs/cache/uploads, scheduled jobs, deployment locks/manifests, proxy backups, database data/admin configuration and backups. Durable data and recovery artifacts have different lifecycles from application releases.

Physical central storage is permissible when its resources have explicit owners, interfaces and lifecycle rules. Avoid an unclassified shared directory or a hidden dependency on a retired parent checkout. Repo ownership does not mean an application runtime user should have write permission to every owned path.

Use separate operating-system identities and environment/database privileges where warranted by the threat model. UI-only processes generally need public configuration and internal routing, not backend provider or migration credentials. Record actual allowed environment keys; never copy a full legacy environment to every service.

Provider enablement, test/live mode, origin and operator flags must survive redeployment. A capability projection is not authorization to switch a provider on. Verify active process configuration without printing secrets; source example files alone do not prove runtime values.

## Reproducible deployment

For version calculation, release PRs, image tags and production hotfix tracks,
read [release-versioning-and-hotfixes.md](release-versioning-and-hotfixes.md).

- Record source revisions, build artifacts, configuration contract and compatible dependency versions. Follow the project's clean/pushed-source policy; do not invent a mandatory GitHub workflow for every project.
- Verify builds from each repo's declared inputs. Preserve versioned packages/SDKs; undeclared sibling source imports or parent runtime files defeat independent checkout/deploy claims.
- Keep private AI setup, caches, credentials, uploads and databases out of source archives. Check tracked/staged files and archive contents; ignore rules do not remove already tracked data.
- Build before switching traffic or process pointers. Health checks include relevant dependencies and the actual public path, not only a static endpoint.
- Serialize changes where needed. Define release/database lock scopes and ordering, avoid nested non-reentrant locks and preserve useful failed-release evidence.

Independent release means compatible changes can target one component. Breaking contracts, schema changes, gateway changes or distributed workflows may need coordinated ordering. Preserve older consumers during an additive transition. Do not promise all repos always deploy in isolation.

## Workers, migrations and cutover

Identify background timers/cron/queues as well as HTTP processes. Before changing financial/stateful workers, drain or pause them according to the workflow and use a lock/lease/idempotency design that prevents duplicate work across old/new versions. Unknown in-flight money outcomes require reconciliation; do not automatically restart a second worker or silently retry a non-idempotent action.

Apply each migration once per intended database/version under the designated ordering, lock and credential policy; support safe retries. Verify live schema/roles before switching dependent releases. Keep migration admin credentials separate from runtime roles. A shared database does not mean each repo should race to run its own copy of the same migration.

Switch only the intended components, preserving unrelated services and host proxy/TLS ownership. Test configuration before a reload. Verify the intended revision, environment, listeners and critical actor journey through the customer hostname. A local upstream pass does not override a public-path failure.

## Rollback versus data recovery

Record a known-compatible prior artifact and its schema assumptions. Ordinary code rollback retains data written since deployment and compatible additive migrations. Do not restore an older database automatically to reverse an application release.

If compatibility is uncertain, stop the unsafe cutover or roll forward with an explicit recovery plan. A database restore is a separately authorized data-recovery decision with loss window, writer coordination and reconciliation. Do not infer rollback compatibility from retained files alone.

## Legacy dependency proof and cleanup

Before stopping or removing legacy directories, inspect actual process command lines/working directories, process units, timers/cron, compose mounts, configuration paths, symlinks, uploads/static assets, backups and migration scripts. Search only the authorized scope. A source grep and green HTTP health response are insufficient.

When authorized, quarantine/rename or stop the old application as a reversible dependency test, then exercise affected reads/writes, auth, assets, uploads, workers and recovery commands. Preserve separate backup/recovery evidence and current durable state. Do not assume renaming automatically retargets a running process.

Inventory exact deletion targets and retained resources. Resolve symlinks and verify ownership/allowed root before mutation. Retention should follow actual compatibility and recovery needs, not a universal count of releases. Clean only task-owned successful staging artifacts automatically; deletion of legacy apps, durable data or recovery evidence is a separate action.

On completion, report source extraction, build independence, deployed revisions, public journeys, worker handover, rollback/restore evidence and retained gaps separately. Preserve a non-Git parent workspace when requested; removing a parent repository is distinct from deleting its child repos or data.
