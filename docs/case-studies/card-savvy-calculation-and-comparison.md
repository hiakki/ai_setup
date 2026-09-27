# card-savvy-india: truthful calculations and usable comparison tables

Reviewed: 28 September 2026. Search terms: card-savvy-india, refunds, CSV import,
unknown rewards, ranking, score, comparison table, sticky context, responsive,
mobile, source links, evidence.

This case combines a calculation review and a later UI verification record.
They cover different parts of the application. The UI record does not close the
calculation findings. No statement import, issuer research or browser test was
rerun for this central review; no personal financial data is included.

## Findings that should change the next implementation

| Concrete source finding | Reusable action | Evidence status |
| --- | --- | --- |
| Absolute-value parsing made positive, negative, parenthesized and credit-marked amounts all positive. | Preserve transaction identity, amount direction and purchase/refund/payment meaning through import and calculation. Do not simply discard all negative rows. | S1 reproduced the parser in an isolated Node VM. The fix and full import journey were outstanding in that record. |
| An unmatched actual card became zero reward and a quantified missed opportunity. | Keep unresolved actual values unknown; count unresolved rows and exclude unquantifiable gaps from confirmed totals. | S1 exercised that branch with a deliberately stubbed scorer. It did not verify issuer rates or a full statement import. |
| A preference bonus entered the same value used for monetary reward totals. | Separate ranking/tie-break preferences from money. Identical earning rules must produce identical monetary results regardless of presentation preference. | S1 records a source finding and proposed correction, not proof the calculation was repaired. |
| Estimates were labelled Actual and Best possible without historical dates and cap state in that path. | Distinguish observed values, estimates and optimization claims. Preserve the applicable rule date and period ledger, or label a limited simulation. | Source review, not current issuer advice. A greedy row winner does not prove the best allocation over a period. |
| Narrow comparison tables could lose card and row identity while scrolling. | Retain comparison context and keep the final column's evidence links visible and keyboard reachable. Test selected-item persistence through navigation. | S2 records responsive browser checks and fixes for single-selection replacement and mobile overlap. |
| Strong presentation evidence could be mistaken for whole-product correctness. | Report calculation, browser, data provenance, accessibility and external-fact verification separately. Use domain/arithmetic review before visual polish. | S2 used synthetic wallet data; it did not retest statement imports, all existing calculations, screen readers or every browser. |

For another comparator, make the score's unit, evidence status, sorting and
uncertainty explicit. A usable table needs both correct values and persistent
row/column context; neither an attractive screenshot nor a large check count
establishes the other.

## Reuse

Search `ai-setup search "card-savvy comparison"`. Read
[Indian card research](../../custom/skills/india-card-research/SKILL.md) for
current official terms and dated arithmetic,
[auditable workflows](../../custom/skills/auditable-business-workflows/SKILL.md)
for source facts versus derived values, and
[usable apps](../../custom/skills/build-usable-apps/SKILL.md) for rendered checks.
Generic comparison lessons also apply outside cards; issuer rules do not.

## Source map and limits

The source directory had **no Git repository** at review time. These are local
document snapshots, not committed or deployed revision claims.

| ID | Source relative to `card-savvy-india/` | Record date | SHA-256 |
| --- | --- | --- | --- |
| S1 | `docs/quality-review.md` | 14 September 2026 | `f31740ad22ad0244bb3ceba0afb43b9f2d972243769f983a696770075e1b71bb` |
| S2 | `docs/explorer-verification.md` | 15 September 2026 | `38fef990d2a645da44a35305d5a88b1f2843e80e4ec66009f6856b01618d06b4` |

Both documents were read in full. Graph coverage excludes this documentation;
direct file reads supplied the evidence. Source reports remain authoritative for
their exact test scope. This case makes no claim of repaired import arithmetic,
current card benefits, financial optimality or accessibility certification.
