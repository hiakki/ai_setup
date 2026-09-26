---
name: auditable-business-workflows
description: Model, implement, or review rule-heavy business workflows involving money, status, eligibility, hierarchies, rewards, invoices, corrections, demo data, and derived calculations. Use when inconsistent rules across UI, reports, seeds, or APIs would create financial or operational risk.
---

# Auditable Business Workflows

Make one rule produce one answer across every surface.

## Workflow

1. Establish the authority order for approved requirements, open assumptions, executable configuration, domain code, and UI copy.
2. Define terms, source events, invariants, eligibility gates, period boundaries, and correction semantics before implementation.
3. Put calculations and state transitions in shared server-side domain functions.
4. Keep source facts separate from derived totals and presentation labels.
5. Version financially meaningful rules or snapshots when historical recomputation must remain stable.
6. Exercise worked examples, threshold edges, reversals, retries, and downstream propagation.
7. Verify agreement among API, UI, reports, exports, seed/demo data, and audit history.

## Non-Negotiable Invariants

- Never invent a missing business rule silently. Record the assumption, scope, and approval owner.
- Account status, ability to participate, ability to contribute upstream, and ability to earn are separate policies.
- Hierarchical placement and referral attribution are separate relationships unless the approved model says otherwise.
- Demo, test, internal, and synthetic records never affect real reports or payouts.
- Where the approved model maps product/order events to volume or rewards, derive them from those source events; manually editing a derived total is not a substitute for a ledger.
- Corrections are explicit domain operations with authorization, reason, impact preview, audit, and idempotency.
- Historical invoices and financial statements use immutable snapshots or revisions, not live mutable catalog/profile data.

## References

- Read [source-of-truth-and-calculations.md](references/source-of-truth-and-calculations.md) for rule hierarchy, derived values, fixtures, and thresholds.
- Read [hierarchy-status-and-corrections.md](references/hierarchy-status-and-corrections.md) for tree relationships, eligibility, propagation, replacement, and deletion.
- Read [financial-artifacts-and-demo-data.md](references/financial-artifacts-and-demo-data.md) for products, invoices, reversals, demo isolation, and realistic seeds.

