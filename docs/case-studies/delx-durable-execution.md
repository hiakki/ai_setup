# DelX: durable intent, uncertain requests and ownership during recovery

Reviewed: 28 September 2026. Search terms: DelX, durable execution, idempotency,
timeout, provider reconciliation, retry, cancellation race, worker lease, journal,
partial completion, accounting evidence.

The source is a software execution/risk audit using a fake exchange. This case
extracts general external-operation and accounting lessons, not trading strategy,
account balances, pricing formulas or a recommendation to place orders. No
exchange requests, transactions or application changes were made for this review.

## The failure mechanism

A timed-out create request could be followed by another create after an order-list
lookup failed. An empty or unavailable list did not prove the first request had
been rejected. Other recovery paths cleared local inventory or released a worker
before external completion was known. These failures concern durable intent and
ownership; changing a button label or adding a generic retry could not fix them.

| Recorded defect and repair | Apply to another external workflow | Verification boundary |
| --- | --- | --- |
| Persist request identity and parameters before the outbound call; reconcile that identity after an uncertain response. | Use the provider's supported idempotency/reconciliation contract. A local identifier alone cannot enforce remote uniqueness. Block a new equivalent mutation while acceptance remains unknown. | Exercise timeout after acceptance, failed lookup and restart with retained intent. Source evidence is fake-exchange regression testing. |
| Clear intent only for documented structured pre-acceptance refusals. | Distinguish proven rejection from unknown acceptance. Do not freeze every ordinary rejected request forever or assume every HTTP error means no mutation occurred. | Verify the actual destination's current contract before defining the refusal allowlist. Do not copy this provider's codes. |
| Manual exit and leg removal retain their pending worker and lease until confirmed completion. | Keep durable ownership while work remains in flight, including shutdown/removal paths. A temporarily empty projection does not prove completion. | Test unresolved earlier creates, late responses and concurrent replacement attempts. |
| Returned data could contain identities outside the requested filter. | Validate identity, side and relevant parameters on every recovered result before attaching it to local intent. | A successful filtered API call is not sufficient evidence that every returned record belongs to the request. |
| Missing terminal quantity was treated as full completion; cancellation races could recreate already consumed inventory. | Preserve unknown quantities. Reconcile authoritative terminal state and actual partial completion before issuing a replacement. | Test partial completion, cancellation races, duplicate updates and missing fields; do not resubmit the original amount blindly. |
| A failed journal write blocks new entries. | Make persistence a prerequisite to externally consequential mutations when recovery depends on that journal. | Test the storage-failure branch, not only successful process restarts. |
| Position estimates and account totals used different evidence bases. | Label the accounting scope and excluded costs. Do not allocate aggregate costs to an individual operation without an attributable ledger. | Reconciled software totals do not establish profit, future outcome or guaranteed execution. |

These patterns are relevant to provisioning, fulfillment and payment integrations
as well as execution systems, but each provider needs its own contract and tests.
Do not transplant exchange semantics into another API.

## Reuse

Search `ai-setup search "delx reconciliation"`. Read
[auditable calculations](../../custom/skills/auditable-business-workflows/references/source-of-truth-and-calculations.md)
and [provider delivery](../../custom/skills/reliable-web-app-operations/references/provider-delivery.md).
For each adopted pattern, identify the target's authority, durable identity,
recovery owner, unresolved state and test through the real application boundary.

## Cache, replay and UI follow-up

Two additional source audits preserve related failures worth reusing:

- A cached score omitted cost inputs from its identity. Shared mutable cached
  rows let another request alter audit values without changing their timestamp.
  Include material inputs in cache identity and isolate per-request results;
  test changed parameters and backward clock movement.
- Chunked time-series acquisition assumed inclusive endpoints and could miss a
  boundary. The recorded fix overlaps/deduplicates identical records and rejects
  conflicting duplicates; only completed intervals are eligible. Requesting a
  window does not prove complete coverage.
- A screening template was treated as evidence for another deployment's inputs.
  Bind evidence to the effective configuration and disclose simulation/runtime
  differences. Freeze acceptance criteria before comparing outcomes and retain
  losses, inactivity and incomplete cases.
- Historical closed records locked settings and displayed old unrealized values
  as though they represented current exposure. Preserve history separately from
  active, closing and unresolved work; test the actual UI against each state.
- A protection check validated identity but missed whether a changed target
  still met the saved constraint. Validate the relevant semantic invariant, not
  just that a related external object exists.

These lessons do not establish investment performance. The source records describe
simulations, a public-data diagnostic and browser checks with intercepted data;
none validates real execution in a new app. Existing green tests had missed the
UI/protection defects until targeted regressions were added.

Additional sources, read in full and clean at the same DelX revision below:

| Source | SHA-256 |
| --- | --- |
| `research/quant-pipeline-audit-2026-09-19.md` | `53b5a9465ffdc8a5ee65e921db5cd5e141d041c9e72c5b99ea5c250208e9c448` |
| `research/cross-engine-audit-2026-09-19.md` | `b2b6033206c10505c5354eefb4faa3e859aed6243becbb808b72e2a02bae3465` |

## Earlier failed assumptions retained

An earlier audit reproduced a requested-duration gate accepting a much shorter
observed replay and counted the same favorable evidence twice. It also found a
public-data fetch failure could prevent otherwise available safety/reconciliation
checks from running. Test actual observed coverage, trace each evidence
contribution once, and keep critical supervision independent of optional data.

The dated follow-up records repairs but retained limitations. Later reporting
requests exposed contention between differently scoped history caches; the
record describes separate caches, bounded refresh outside request locks and
unknown loading states rather than fabricated zero values. Read the later audit
sections above before treating an early unresolved finding as current behavior.

Source: `DelX/research/profitability-audit-2026-09-15.md`, clean at the revision
below, SHA-256 `1955651dd6e351609bd9ccc4a5ee50fe8b58dd85a36731baefa042ceec88a67d`.
Reviewed assessment, live-path findings, verification and remediation follow-up;
the intervening legacy-engine/remediation-order sections were not reviewed in
this pass. Source-reported reproductions used synthetic or frozen public inputs,
not live account verification. No account facts are exported here.

## Original source and evidence limits

Source: `DelX/research/execution-risk-audit-2026-09-19.md`, read in full, clean
tracked at `DelX@bbcab5684ac3bddee22b110ca6a45a75fb6b1950`.
SHA-256: `6eb66a5c554e6de14e194dba1f2ec78688204614080e6818cbf8e0b2d192dfab`.
Graph coverage recorded no issue for this path; this review read source text.

The audit reports 257 focused passing tests, all exchange interactions faked.
That is historical test evidence, not a fresh run or a live-provider validation.
It explicitly made no real orders, production changes or deployment. Full runtime
verification belonged to a separate release process and is not assumed here.
