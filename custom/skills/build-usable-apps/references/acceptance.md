# Evidence that a user can complete the task

Select relevant rows; do not turn this into a mandatory full-suite rerun for
every small change. Test the cause of the reported defect and nearby consumers
of any changed shared component.

| Area | Exercise | Observable acceptance |
| --- | --- | --- |
| First visit | Start with no records/data. | Purpose and next action clear; no fake ratings, earnings or empty provider statuses. |
| Saved progress | Leave before/after each relevant save; expire the session and return. | No duplicate account, no nonexistent-password demand, honest saved state and usable resume path. |
| Verification | Invalid/expired/replayed code, resend, double-click, concurrent creation. | No unverified activation or duplicate side effect; actionable retry and consistent server state. |
| Authentication | Wrong role entry, internal return URL, external return URL, held account. | Correct existing role/destination preserved; no restriction or redirect bypass. |
| Form failure | Server validation, slow request, network interruption, upload rejection. | No false success; entered valid details retained; error identifies a useful correction. |
| Approval | Missing evidence, correction, completed checks, one approval. | Blocker names exact next step; approval enables the promised work once. |
| Approved edits | Direct/tampered request, stale session, harmless formatting, ordinary setting. | Protected changes rejected; allowed updates retain approval; correction path works. |
| Tables | All role tabs; empty, one and many rows; long text; zero and large amounts. | Relevant columns, correct singular/plural labels, understandable no-data values. |
| Alignment | Every sortable header inactive/ascending/descending, including wrapping. | Header text and body content share the intended edge; badges use outer edge; numeric values align right. |
| Open actions | Open/close menu or modal for first/last/long row. | No accidental table resizing or shifted columns; selected record stays clear. |
| Responsive | Phone, tablet with sidebar, desktop, zoom and long content. | Main action reachable; no clipped controls or accidental page overflow; deliberate table scrolling remains usable. |
| Modal | Keyboard open, Tab/Shift+Tab, Escape, close button, nested close. | Accessible name, background inert, focus visible and restored; child close does not dismiss parent. |
| Feedback | Success, error, loading, retry and disabled states. | Clear outcome/next action, no contradictory badges, no misleading completion. |
| Mail | Retry burst, provider refusal and authorized real delivery when in scope. | Server throttling works; truthful queue/delivery history; sender/receipt verified separately. |
| Deletion | Flag off/on, permission denied, linked records, confirmation/cancel. | UI and server agree on eligibility; cancelled operation changes nothing. |
| Payments | Real contract plus authorized sandbox/live journey, replay and reconciliation. | Separate collection/refund/payout evidence; no transaction-readiness claim from mocks. |
| Release | Exact commit/build, actual environment/schema, public URL and signed-in affected flow. | Settings preserved, failure has rollback, local results not misreported as live acceptance. |

## Browser measurements

Use actual rendered text bounds (for example a DOM Range), not just enclosing
cell rectangles. A padded header button can misalign text while every table
column rectangle is perfect. Choose a small documented tolerance appropriate to
the layout and browser rendering; do not relax it to hide a visible mismatch.

Compare row/cell positions and dimensions before, during and after opening an
action. Check whether the primary action is inside the available viewport;
“the page has no overflow” can still pass when a nested table hides Actions.
Test compact and full-table presentation around the real container breakpoint,
not only familiar device widths. One viewport size does not cover all sidebar
or role-column combinations.

Inspect a text action while actually hovered, pressed and keyboard-focused.
Correct text alignment must not leave the label touching the edge of its hover
surface. Keep visual padding and a usable hit area while preserving the column
anchor; test their bounds as separate properties. Resting screenshots alone miss
this defect, and hiding keyboard focus is not a valid cosmetic fix.

Inspect a batch of closed/open screenshots yourself. Functional assertions can
pass while labels, visual hierarchy, density and readable grouping remain poor.
After a corrective batch, regenerate relevant captures; do not review stale ones.

For native dialogs, assert background application controls cannot receive focus,
the modal remains open, its controls are reachable and Escape restores focus.
Do not add a custom focus trap just because a browser temporarily reports BODY
or browser chrome as active at a native Tab boundary.

Keyboard testing does not establish screen-reader accessibility. A screenshot
does not establish touch behavior, performance or provider integration. State
which modalities were actually exercised.

## Lightweight evidence record

For each affected journey, record: initial state → action → expected user-visible
outcome → actual persisted outcome → artifact/result → environment and date.
Add only material gaps. Keep these levels separate:

1. Implemented code and static checks.
2. Unit/mocked behavior.
3. Rebuilt local app with real test database/browser.
4. Provider sandbox or explicitly authorized live provider test.
5. Deployed commit, public-path and signed-in live verification.

A high aggregate passing-test count cannot replace a missing critical journey.
Do not claim a level whose specific evidence is absent. Empty production queues
are valid empty-state evidence, not evidence for populated review actions.
