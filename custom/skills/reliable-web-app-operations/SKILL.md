---
name: reliable-web-app-operations
description: Design, implement, debug, or audit repeatable web application operations, release versioning, immutable artifact promotion, manifest-driven Compose/Kubernetes deployment, environment configuration, database lifecycle and recovery. Use for central CI/CD, deployment runbooks, backups, provider delivery, observability and legacy retirement.
---

# Reliable Web App Operations

Build an operational path that a new machine and an existing production host can both run safely.

This skill covers setup, release and operational instrumentation. For a causal
incident investigation, use `sre-incident-investigation` when available; the
reference below still provides a standalone initial diagnostic workflow. Keep
project-specific process-manager commands and provider settings in its runbooks.
This skill grants no deployment, restart, restore, provider-spending or external
write permission. Confirm existing authorization before any such action.

## Workflow

1. Identify the supported operating systems, runtime, process manager, reverse proxy, data store, and external providers.
2. Separate command intent: prerequisite setup, application deployment, monitoring setup, health/status, proxy reload, backup, and restore must not silently invoke one another.
3. Define one environment contract. Sync missing example keys without overwriting operator values, validate URL and credential shapes, and fail before mutating runtime state.
4. Make setup idempotent. Detect installed capabilities and package-manager differences before installing or restarting anything.
5. Verify the real path after a change: process, localhost endpoint, public URL, provider request, persistence, and recovery behavior as applicable.
6. Report evidence levels separately: static checks, local runtime, sandbox provider, deployment, and live end to end.

## Non-Negotiable Invariants

- Monitoring setup must not deploy or restart the application.
- A deploy must preserve explicit environment flags and existing secrets.
- Health checks must test required dependencies, not only return a hard-coded success.
- A provider accepting a request is not proof of delivery or settlement.
- Logs must retain actionable error context while excluding credentials and personal or financial data.
- Metrics use bounded labels. Put request IDs, exact errors, and arbitrary identifiers in logs or traces.
- Destructive seed, reset, restore, and migration commands fail closed in production.
- Every recovery procedure includes a verification step and a safe stopping condition.

## References

- Read [deployment-contract.md](references/deployment-contract.md) for environment synchronization, command boundaries, and release evidence.
- Read [central-container-builds.md](references/central-container-builds.md) for central CI/CD ownership, per-app manifests, shared Docker build profiles, image size and hardened runtime verification.
- Read [service-release-and-retirement.md](references/service-release-and-retirement.md) for multi-repository deployment, worker handover, runtime resource ownership and legacy cleanup.
- Read [release-versioning-and-hotfixes.md](references/release-versioning-and-hotfixes.md) for central version automation, release provenance, production hotfix branches and partial publication recovery.
- Read [portable-deployment.md](references/portable-deployment.md) for manifest-driven Compose/Kubernetes adapters, immutable promotion, worker draining and cross-target recovery.
- Read [database-operations.md](references/database-operations.md) for database lifecycle ownership, migration/schema verification, locking, backups and restore rehearsals.
- Read [observability-and-incidents.md](references/observability-and-incidents.md) for telemetry layers, user-reported slowness, cardinality, and incident diagnosis.
- Read [provider-delivery.md](references/provider-delivery.md) when integrating email, SMS, storage, payment, or other external providers.
