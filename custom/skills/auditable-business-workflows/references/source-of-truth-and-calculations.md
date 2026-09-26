# Source Of Truth And Calculations

## Authority Map

Define and document an order similar to:

1. latest approved business decision;
2. signed product/rule specification;
3. assumptions and open-question register;
4. executable rule configuration;
5. shared domain implementation;
6. adapters, reports, seeds, and UI.

When two authorities conflict, stop financial implementation and surface the exact conflict. Do not “fix” one screen independently.

## Modeling

Separate:

- source facts: purchases, payments, refunds, placements, approved adjustments;
- derived values: totals, ranks, slabs, eligibility, earnings;
- projections: estimates and next-target guidance;
- settled facts: approved statements and paid amounts.

Compute derived values through one domain path. If performance requires persistence, store rule version, source period, and reconciliation data so the value can be reproduced.

## Test Fixtures

Include:

- smallest valid case;
- exactly at each threshold;
- one unit below and above;
- balanced and unbalanced hierarchy cases;
- empty branch/group;
- ineligible participant whose contribution still propagates, when approved;
- refund/reversal;
- repeated/replayed command;
- rule-version boundary;
- realistic multi-actor examples rather than one actor with impossible volume.

Assert both the final number and the explanatory components shown to users.

## Terminology

Use customer language in UI and stable domain language in code. Maintain an explicit translation map where internal coordinates or legacy terms differ. A label change is incomplete until forms, trees, reports, exports, notifications, tests, and docs agree.

