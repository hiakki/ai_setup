# Permissions, Audit, And Destructive Actions

## Permissions

- Define capabilities by action, not broad page access alone.
- Enforce permissions at the server mutation boundary.
- Render navigation and controls from the same capability model where practical.
- Test allowed and denied paths for every mutating role.
- Treat impersonation as the original operator acting through a target view; do not grant target credentials or lose the operator session.

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

