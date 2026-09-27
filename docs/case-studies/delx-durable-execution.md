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

## Source and evidence limits

Source: `DelX/research/execution-risk-audit-2026-09-19.md`, read in full, clean
tracked at `DelX@bbcab5684ac3bddee22b110ca6a45a75fb6b1950`.
SHA-256: `6eb66a5c554e6de14e194dba1f2ec78688204614080e6818cbf8e0b2d192dfab`.
Graph coverage recorded no issue for this path; this review read source text.

The audit reports 257 focused passing tests, all exchange interactions faked.
That is historical test evidence, not a fresh run or a live-provider validation.
It explicitly made no real orders, production changes or deployment. Full runtime
verification belonged to a separate release process and is not assumed here.
