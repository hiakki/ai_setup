# Hierarchy, Status, And Corrections

## Relationships

Model different meanings separately:

- referrer/proposer: who introduced the participant;
- placement parent/sponsor: where the participant sits in a constrained hierarchy;
- owner/manager: who administers the account;
- beneficiary: who receives a financial effect.

Do not overload one foreign key for several meanings. Validate capacity, self-reference, cycles, and cross-tenant boundaries on every mutation.

## Status Policy

Represent status effects as a policy or transition table instead of scattered conditionals.

| Concern | Example questions |
| --- | --- |
| Access | Can the account sign in? |
| Participation | Can it add or receive descendants? |
| Own contribution | Does its purchase create personal volume? |
| Upstream propagation | Do valid descendant events pass through it? |
| Earnings | May it receive payout for the period? |
| Review | Is office approval or fraud review required? |

Changing one concern must not accidentally change the others.

## Corrections

Define replacement semantics before coding:

- Does the old node keep descendants?
- Does the replacement inherit direct children or the complete subtree?
- Does the old node become unplaced, archived, or independent?
- Which historical calculations remain unchanged?
- Which current-period values recompute?

Perform a dry-run impact calculation, authorize, validate again in the transaction, mutate atomically, recalculate affected ancestors, and write one descriptive audit event. Block account deletion until protected connections and artifacts are resolved.

