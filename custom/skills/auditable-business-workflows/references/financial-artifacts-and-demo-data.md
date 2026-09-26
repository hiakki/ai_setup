# Financial Artifacts And Demo Data

## Product And Order Boundary

- Catalog owns product identity, SKU, price, tax, volume mapping, availability, and media.
- An order line stores an immutable snapshot of financially relevant product fields.
- The server resolves price and volume from the catalog; never trust client-supplied calculated values.
- Product purchase and hierarchy/rank units are different concepts unless the approved plan explicitly links them.
- Refunds and corrections create reversal or adjustment entries rather than silently rewriting history.

## Invoices And Statements

- Preview is side-effect free.
- Publication creates a customer-visible record.
- Regeneration creates or replaces the current visible revision according to a documented uniqueness rule while preserving office audit history.
- Mature ecommerce/accounting flows use voids, credit notes, and revisions instead of deletion.
- Transitional manual deletion, if allowed, is role-restricted, confirmed, and audited.
- Historical documents render from saved snapshots, including seller identity, buyer identity, lines, taxes, totals, date, numbering, and signature policy.

## Demo And Test Isolation

- Give synthetic accounts an explicit classification outside business status.
- Exclude them in the shared reporting/query boundary, not independently on each dashboard.
- Prevent synthetic activity from creating real payouts, organization totals, notifications, invoices, or analytics unless the test explicitly targets those systems.
- Guard destructive reseeding with both environment and disposable-data flags.

## Realistic Seeds

Seed from permitted actor behavior: one participant, one eligible purchase/event, and real hierarchy propagation. Do not simulate organization growth by assigning impossible personal totals. Provide named scenarios for balanced, unbalanced, threshold-miss, threshold-touch, inactive/provisional, refund, and deep-tree cases.

