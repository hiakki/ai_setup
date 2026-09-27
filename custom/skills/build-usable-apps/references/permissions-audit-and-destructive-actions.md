# Permissions, Audit, And Destructive Actions

## Permissions

- Define capabilities by action, not broad page access alone.
- Enforce permissions at the server mutation boundary.
- Render navigation and controls from the same capability model where practical.
- Test allowed and denied paths for every mutating role.
- Treat impersonation as the original operator acting through a target view; do not grant target credentials or lose the operator session.

## Admin-managed access and test accounts

- When asked to follow an existing elevation flow, inspect what it actually does.
  An immediate change by account email and an invitation requiring acceptance
  are different workflows; match the agreed behavior and button wording.
- Put rare privileged classification changes in the relevant admin management
  surface. Do not add a self-service switch or repeat it in ordinary account
  menus merely because those components already exist. Explain restrictions to
  affected users without exposing the privileged control.
- For conversion of an existing account, normalize and resolve its identifier
  on the server. Unknown accounts must not silently create placeholders. Keep
  account role, approval and QA classification separate unless the agreed
  transition explicitly changes them.
- Recheck current operator authority and target state at the mutation boundary,
  including stale sessions and replayed requests from removed UI controls.
  Invalidate or refresh affected sessions when access or financial restrictions
  change. Record who changed which account and the outcome.
- For QA financial and data isolation, use the relevant demo/test guidance in
  `auditable-business-workflows` when available. A hidden checkout button is
  not a payment boundary.
- Do not present a test workflow's positive approval state as real document
  verification or financial eligibility. Show the test classification and role;
  retain actionable hold/pending/review blockers. Check list, detail and payout
  copy together. Preserve server review state and restrictions unless changing
  them is explicitly part of the requirement.

## Audit Events

Record:

- stable action type;
- actor and role;
- target;
- timestamp and request/correlation ID;
- outcome;
- changed sections or field names;
- reason for sensitive corrections;
- provider reference when applicable.

Generate changed-field descriptions from a generic before/after diff with a maintained sensitivity-aware label map. Future fields should appear automatically instead of requiring one audit branch per field. Never log secret or sensitive values.

Distinguish legacy records with unknown actors from system-initiated automation. Do not label both as “system.”

## Corrections And Deletion

- Show current state and proposed state before a relationship correction.
- Explain downstream consequences before confirmation.
- Require a reason for destructive or financially meaningful corrections.
- Separate disconnect, replace, detach descendants, delete, void, and archive; they are different operations.
- Block deletion while protected relationships or financial artifacts remain unless an approved migration workflow resolves them.
- Prefer archive, void, reversal, or credit-note behavior once records participate in a mature transactional system.
