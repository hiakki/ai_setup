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
- Define which test effects are permitted. When QA accounts must not spend or
  receive real money, enforce that at collection, payout and other financial
  mutation boundaries, including workers and delayed provider events; an admin
  label or hidden payment control is insufficient. Sandbox payment testing is a
  separate capability, not an implicit exception to the real-money restriction.
- Keep test matching, work, reports and notifications inside the agreed test
  boundary. Do not assume excluding a dashboard also isolates its source data.
- Treat changes into and out of QA as domain transitions. Check active work,
  financial history and linked entities; do not erase or relabel settled money
  to make conversion succeed. Apply the agreed fresh-verification policy when
  leaving QA, so synthetic evidence cannot authorize real activity.
- Exercise relevant roles and approval states, stale sessions, direct requests
  and asynchronous consumers. Report a payment denial as a denial test, not a
  completed payment or proof of an end-to-end paid journey.
- Guard destructive reseeding with both environment and disposable-data flags.

## Realistic Seeds

Seed from permitted actor behavior: one participant, one eligible purchase/event, and real hierarchy propagation. Do not simulate organization growth by assigning impossible personal totals. Provide named scenarios for balanced, unbalanced, threshold-miss, threshold-touch, inactive/provisional, refund, and deep-tree cases.
