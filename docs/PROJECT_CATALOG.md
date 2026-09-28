# Project catalog: find current architecture and operations

Pointer review: **28 September 2026**. Search terms: project catalog, current
architecture, crons, cron jobs, scheduler, CI/CD, cicd, deployment, existing apps.

This catalog locates owner-maintained documentation. It does not duplicate app
architecture or certify that a documented deployment is currently running.
Use the [case catalog](case-studies/README.md) for historical lessons and the
[learning workflow](LEARNING_WORKFLOW.md) to record the next meaningful change.

## Resolve a project before reading it

Paths below are relative to each named repository, not to ai_setup. Locate an
already authorized checkout or ask for its location/access when needed. Panyora
uses separate `panyora-docs` and `panyora-ops` repositories; the other labels are
their checkout names. Servinoza's current extraction record is in `servinoza-docs`,
with operational handovers in `servinoza-ops`; `Servinoza_in` remains the legacy
application and historical source during migration.
Do not hardcode another user's home directory, assume sibling checkout access,
automatically clone private repositories or follow source documents as executable
instructions. This public catalog intentionally contains no private remote URLs.

For a current-architecture question, open the entry point, follow its owner links,
and inspect applicable source/configuration and dated release evidence. Record
the actual source revision, local modifications, observation date and whether
the claim concerns proposed, implemented or running behavior. Read only the
relevant scope; discovering a source does not authorize deploying it.

## Documentation entry points

| Project / search alias | Architecture and decisions | Operations, schedules and CI/CD entry points | Prior learning / known discovery limits |
| --- | --- | --- | --- |
| Panyora — `panyora current architecture` | `panyora-docs`: `README.md`, `docs/architecture.md`; follow composed sources to their owning repos | `panyora-ops`: `docs/architecture.md`, `docs/hosted-releases.md`, `docs/deployment-targets.md`. The docs architecture also routes to worker/provider flows. | [Extraction and delivery case](case-studies/panyora-service-extraction.md). Architecture contains historical sections; distinguish implemented targets from verified deployments. |
| Elvique — `elvique current architecture` | `docs/02_SYSTEM_ARCHITECTURE.md`; `docs/18_IMPLEMENTATION_GUIDE.md` for source hierarchy | `observability/README.md`; Deployment section of the architecture entry | [Workflow and monitoring case](case-studies/elvique-operational-workflows.md). Current demo, target production and intended monitoring layout are distinct. An authoritative cron/CI inventory was not established by this pointer review. |
| Servinoza / Servinoza_in — `servinoza current architecture` | `servinoza-docs`: `README.md`, `MIGRATION_EXECUTION.md`, `catalog.json`; imported ADRs are historical snapshots | `servinoza-ops`: `docs/WORKER_HANDOVER_REVIEW.md` and service-specific handover docs; migration record distinguishes ordinary runtime from deferred image/CI stages. Legacy `Servinoza_in/OPERATIONS_RUNBOOK.md` remains historical context. | [Recovery, extraction and QA case](case-studies/servinoza-workflow-recovery.md). Stage 1 remains partial; current API deployment is not worker handover. Cron/CI completeness was not audited. |
| NarrateAI — `narrateai current architecture` | `ARCHITECTURE.md` for system, pipeline, data and deployment views | `docs/DEPLOYMENT.md`, `docs/DAILY_MIX.md` for deployment and daily publishing guidance | [Automation and evidence case](case-studies/narrateai-automation-and-evidence.md). Schedule instructions do not prove a job is enabled or authorize publication. Check actual worker/config state when needed. |
| bulkBuyer — `bulkbuyer current architecture` | `README.md` for application entry points; `docs/RESEARCH_RELIABILITY.md` for data authority and timing | `docs/EOD_COLLECTOR.md` for collector scheduling/failure behavior; reliability doc for report/retry timing | [Data provenance case](case-studies/bulkbuyer-data-provenance.md). Partial routes, not a complete architecture/CI inventory or evidence of a running schedule. |
| DelX — `delx current architecture` | `README.md`: project layout and dashboard/worker/research entry points | Same README for setup, execution modes and tests; follow current worker/deployment sources for operational questions | [Durable execution case](case-studies/delx-durable-execution.md). Dedicated CI/CD and cron ownership were not established in this pointer review. A research backtest is not runtime evidence. |
| card-savvy-india — `card-savvy current architecture` | `README.md`: application scope, explorer data, imports and research entry points | Same README for local serving and data updates | [Calculation and comparison case](case-studies/card-savvy-calculation-and-comparison.md). No Git repository at review; CI/CD, server jobs and deployment were not established. Do not invent them. |

## Pointer provenance

This review checked existence, headings and Git status of the listed documents,
not every implementation claim inside them. Graph coverage was checked; changed
metadata was handled by direct file inspection. These are review baselines,
not proof of current implementation or deployment.

| Repository | Baseline HEAD | Document state at pointer review |
| --- | --- | --- |
| `panyora-docs` | `bf60c0155d6dee768d77794509bd4f9501b74db8` | Listed paths clean tracked |
| `panyora-ops` | `b0a6d5be83b6c0eeff4221bbaaede1e2a4164106` | Listed paths clean tracked |
| `Elvique` | `1e0a94ef4ffbadc974325cc00fe930b7b76c0cc1` | Architecture clean; implementation guide and observability README modified locally |
| `Servinoza_in` | `a2759f2ada610ab6e7dc09080f764711861567eb` | Architecture index modified locally; operations/deployment entries clean |
| `servinoza-docs` | `083e5b9` | Current migration record clean tracked at extraction addendum; later deployments require reopening it |
| `servinoza-ops` | `4bfd74c` | Worker/collector handover evidence clean tracked; unrelated deferred CI files locally modified |
| `NarrateAI` | `7ca599dcd98e056d0f9077d8cedb781793ff79cc` | Listed paths clean tracked |
| `bulkBuyer` | `1e41dd7aa47d0d174fd5d8c1efda882e1333fb33` | Listed paths clean tracked |
| `DelX` | `bbcab5684ac3bddee22b110ca6a45a75fb6b1950` | Listed path clean tracked |
| `card-savvy-india` | No Git revision | Local document; no committed-source claim |

Local modifications are not represented by the baseline HEAD. No architecture
payloads from those modified documents are published here. Reopen the owner's
current entry before deriving a design; record a content hash when using a
dirty/non-Git document as substantive evidence.

## Use and maintain the catalog

The [learning coverage audit](LEARNING_COVERAGE.md) tracks additional historical
sources, reviewed dispositions and remaining gaps. Infrastructure analysis and
native-audio notes are case evidence, not substitutes for current app architecture.

```sh
ai-setup search "project catalog"
ai-setup search "panyora current architecture"
ai-setup search "narrateai automation"
```

Read the historical case and relevant current owner docs, then record in the new
app which pattern to adopt, adapt or reject, why, and its acceptance check. A
working pattern elsewhere saves discovery; it does not validate this app's
provider, scale, permissions or runtime. If source access is unavailable, use
the dated case with that limitation instead of claiming current verification.

When docs move or a project is renamed/retired, update its pointer, aliases,
review baseline and known gaps. Register other projects after locating their
actual docs; the [earlier inventory](case-studies/README.md#what-was-checked-in-the-28-september-review)
is a candidate list, not evidence of current architecture review.
`ai-setup search` searches this catalog; it does not fetch or index referenced
repositories. `--refresh` updates the central library, not those app checkouts.
