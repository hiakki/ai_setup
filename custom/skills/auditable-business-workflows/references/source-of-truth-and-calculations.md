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

## Across Service Boundaries

One authority does not require a generic shared-code directory or a single repository. Identify the owner of each fact and state transition, then expose versioned interfaces or projections. Keep calculations and mutations that require one atomic transaction together unless a tested concurrency, idempotency, compensation and reconciliation protocol replaces that transaction.

Authentication, tenant membership, location/field access and subscription eligibility are separate policies. A provider transport service may verify signatures or call payment APIs while invoice, order and entitlement outcomes remain owned by their domains. Document transitional shared-database reads and compatibility adapters instead of claiming full isolation from directory structure.

Test cross-service retries, duplicates, timeouts, cancellation/refund races and stale projections when those boundaries change. Preserve immutable invoice/order snapshots and money already moved; a code rollback or administrative correction must not erase legitimate history.

## Modeling

Separate:

- source facts: purchases, payments, refunds, placements, approved adjustments;
- derived values: totals, ranks, slabs, eligibility, earnings;
- projections: estimates and next-target guidance;
- settled facts: approved statements and paid amounts.

Compute derived values through one domain path. If performance requires persistence, store rule version, source period, and reconciliation data so the value can be reproduced.

## Evidence, units and uncertain external operations

Keep ranking preferences separate from monetary values, missing observations
separate from observed zeros, and data eligibility separate from model validity.
Retain the applicable rule date, observation cutoff and actual collection time
when reconstructing historical results. A backfilled observation must not become
a supposedly prospective decision. Preserve credit/refund direction through
imports; an absolute-value parser can silently manufacture spend.

When a mutation can be accepted despite a lost response, persist request identity
and parameters before calling the provider. Reconcile exact identity under the
provider's supported contract; do not infer rejection from an empty or failed
list lookup. A local ID alone does not guarantee remote idempotency. Separate
documented pre-acceptance refusal from uncertain acceptance. Retain recovery
ownership until earlier in-flight work is resolved, and reconcile partial
completion before replacement. Test failed journal writes, response loss,
restart, cancellation races and missing terminal quantities when applicable.

## Agreed schedules and incremental charges

Keep hard availability/safety limits separate from paid allowances: payment must
not override an unavailable window. Validate dependent configuration together
(for example, an after-hours transport rule needs a defined base-hours band).
Examples from competing products are hypotheses, not approved operating policy.

Preview on the owning server and bind consent to the exact evaluated revision,
actors and assignment. Snapshot dated windows, timezone, rule basis, rate, units,
recipient and total. Recheck pending proposals; preserve already accepted prices
and idempotent outcomes when configuration later changes. Historical untimed
agreements need an explicit compatibility path, not invented dates or fees.

For additional scope, assess existing plus proposed windows against daily limits,
thresholds and once-per-booking/night rules. Price only the authorized increment;
do not charge earlier scope twice or retrospectively reprice it. Aggregate rounding
at the policy's declared scope so splitting equivalent windows does not change
the fee. Assert the explanatory minutes/components as well as the final amount.
Define an opening-day key for overnight work rather than silently splitting at
midnight. Schedule validation alone does not reserve capacity across bookings.

Validate the actual producer payload through every consumer schema, then exercise
the real agreement/extension persistence actions and duplicate acceptance. Mocked
owner or payment facts must remain labelled: database success does not establish
provider settlement, public browser behavior or installed-device acceptance.
See the [16 October scheduling case](../../../../docs/case-studies/servinoza-workflow-recovery.md#16-october-2026-agreed-schedules-and-incremental-allowances)
for reproduced failures and bounded evidence.

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
