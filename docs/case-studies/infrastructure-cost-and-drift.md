# logging_cost and istio_issues: cost assumptions and configuration drift

Reviewed: 28 September 2026. Search terms: logging_cost, istio_issues, logging,
ClickHouse, cost POC, write amplification, Helm, configuration drift, infrastructure.

These are sanitized lessons from two local reports. No cloud account, cluster,
bill or production configuration was inspected for this publication. Private
resource names, addresses, charges, volumes and configuration values are omitted.

## A cost estimate missed the workload shape

The logging_cost retrospective reports a proof of concept based mainly on data
volume, compressed storage and nominal machine sizing. Later support analysis
attributed unexpectedly high compute use to small insert batches, background
merging, derived-table writes and active replicas. The original support artifacts
were not independently inspected in this review. [S1]

Preserve these decision changes when assessing another data migration:

- Measure ingest frequency, batch size, write amplification, background work and
  query shape separately from retained bytes. Identify all physical write targets.
- Compare the whole ingestion path. A fast handoff to a managed collector is not
  the same workload as inserting directly into an analytical database.
- Separate live debugging, searchable retention and archival requirements. Model
  their costs and operational consequences without promising one universal stack.
- Verify which billing dimension a proposed optimization actually changes.
  Reducing retention is not automatically a reduction in ingestion or compute.
- Treat a revised estimate as a proposal until a representative workload and
  observed bill support it. Record an explicit resource/budget ceiling where the
  project requires one; do not promise an unattested savings percentage.

The source proposes tuning and alternative layouts, but does not supply a
completed before/after savings validation. Its prices, product tiers and tuning
values are not current recommendations. Recheck official provider documentation,
actual account capabilities and the target workload before applying them.

## Git values were not the effective deployed configuration

The Istio report compares source settings with reported deployed values and finds
out-of-band changes, including runtime resources and control-plane options. It
also warns that an older production configuration file might itself be stale. [S2]

The transferable lesson is to compare source, release inputs and effective
runtime state before a redeployment. Determine ownership for intentional
overrides; review the planned render/diff and verify the resulting runtime. Do
not indiscriminately copy live state back into Git or assume a checked-in file
proves current production state.

This case does **not** endorse the report's version-specific tuning, low-risk
ratings or asserted OOM causal chain. Those require current compatibility
research, causal evidence and an authorized rollout with outcome checks. A drift
finding and a proposed rollout are not proof of a repaired incident.

## Provenance and reuse

Both source directories had no Git revision. Exact local document identities:

| ID | Source relative to its project | SHA-256 |
| --- | --- | --- |
| S1 | `logging_cost/clickhouse_cost_poc_misses.md` | `1a136444614950ef50f86dfe4b7bf7da9689b56b96955d6ade36ee7468ade720` |
| S2 | `istio_issues/HELM-DRIFT-REPORT.md` (dated 19 March 2026) | `d83a3b7ad214727ff9d72904569ffbca3b66c53c1f7a9301773bb3e0df0ac793` |

The documents were read directly in full. This is attributed historical analysis,
not a fresh provider or infrastructure audit. Search
`ai-setup search "logging_cost drift"` and read
[reliable operations](../../custom/skills/reliable-web-app-operations/SKILL.md).
Adopt the measurement and drift checks where appropriate; reject unverified
causal, savings and compatibility claims as a basis for automatic rollout.
