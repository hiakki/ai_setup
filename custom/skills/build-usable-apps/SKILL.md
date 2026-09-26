---
name: build-usable-apps
description: Build or revise application workflows with clear user states, shared UI rules, recoverable onboarding, usable admin reviews and browser-verified responsive interactions. Use for new apps or substantive form, dashboard and management-screen work; adapt to the product rather than importing a marketplace workflow.
---

# Build usable apps

Make the intended task obvious, preserve work when something fails, and verify
the rendered interaction. A polished screenshot, a shared button library and a
large test count are each insufficient on their own.

This skill is portable: keep this folder and its references together. It needs
no particular framework, paid tool, provider, global configuration or agent team.
For an existing app, preserve its brand and useful components. For a new app,
choose a coherent visual direction suited to its audience and establish its
shared rules before implementing several independent pages.

## Start with the user's job and the actual business model

Read the brief and existing decisions. Resolve routine choices yourself; ask
only about missing information that materially changes the workflow. Do not
make the user rediscover requirements they already supplied.

Write a short design contract in the app's existing documentation:

| Concern | Record before implementing |
| --- | --- |
| People and outcomes | Roles, their common tasks, and the next useful action after login. |
| State and access | What each state means, who can change it, and what it enables. |
| Inputs | Required, optional and conditional fields; source, validation, save point and edit rules. |
| Recovery | What persists after refresh, session expiry, resend, failed save and return visits. |
| Appearance | Tokens, shared controls, shell/navigation, density, typography and responsive behavior. |
| Dependencies | Provider capability actually needed, account eligibility, failure path and simpler alternatives. |
| Evidence | A few meaningful user journeys and visible outcomes that establish acceptance. |

Scale the contract to the task; a small fix needs a small amendment, not a new
architecture project. Distinguish an explicit requirement, an assumption and a
future proposal. Do not invent additional approval actors or mandatory services.
Identify the domain's own critical rules as well; these references are not a
complete specification for scheduling capacity, children's data or other
product-specific concerns.

If payments are involved, draw customer collection, merchant settlement,
commission, refunds and recipient payouts separately. Check the customer's
actual provider capabilities before requiring a provider product. A valid API
key is not proof of product eligibility. Verify the real SDK/request/response
contract; never present a mocked payment as proof of funds moving.

## Design the state model before the form

- Separate possession of an account, verified contact, completed details,
  operational approval, availability and individual transaction status. They
  may be different internal facts; surface only distinctions the user needs.
- When approval means ready to work, one authorized approval should complete
  its actual prerequisites and enable that outcome. Do not present several
  apparently independent approvals for the same decision. Keep genuinely
  independent legal/provider requirements only when verified and applicable.
- Every blocked action needs a specific cause and an accessible next step.
  Prefer “Bank proof is missing — add a document” to “Waiting for all checks.”
  A completed step must open its current version, not a superseded record.
- Progress indicators need readable states and navigation to the relevant
  step. Color, a fraction, or a disabled button alone does not explain progress.
- Define the server transition with the UI transition. A disabled control is
  not an authorization check. Avoid states that say Approved while the intended
  task is silently blocked by a contradictory internal flag.

For authentication, sensitive edits, uploads, messaging, payments or deletion,
read [workflow-patterns.md](references/workflow-patterns.md) for the relevant
pattern. Do not introduce those features merely because this skill mentions them.

## Build a small shared design system

- Centralize semantic colors, text styles, spacing, control sizes, radius and
  focus behavior. Use shared button/link, field, status, dialog, disclosure and
  table-sort controls where those patterns repeat. Extend a shared variant for
  an actual recurring need; avoid per-page copies of control appearance.
- Pages own composition, data and business decisions. Do not force admin,
  customer and provider journeys into one giant configurable component.
- Give each screen an obvious primary task. Secondary and destructive actions
  remain available with proportionate prominence. Use ordinary language rather
  than database statuses, provider mode flags or internal implementation names.
- A home screen should answer “Where am I?” and “What can I do next?” Show the
  role-relevant information; include a greeting/avatar when the brief calls for
  one, without introducing a photo requirement. Distinguish no data
  from a zero value: no ratings yet is not a zero-star rating.
- Use persistent labels and field-level feedback. Related labels, controls and
  helper text belong on consistent layout tracks. Required fields must match
  server requirements. Do not request data the app can reliably prefill.
- Keep keyboard focus visible once, not as stacked competing rings. Include
  high-contrast behavior. A native semantic element is a good default, but test
  its actual behavior with the application's CSS and framework.

## Make management screens scannable and actionable

- Preserve search, filters, pagination and selected-record context after actions.
  Large relationship selectors need bounded search results and protection against
  stale responses. Bulk actions need explicit selection and visible partial failures.
- Start queues with compact summaries. Open the selected record in an accessible
  dialog, drawer or detail page when detailed review needs space. Choose based
  on the task; do not make every message or interaction a modal.
- Use truthful, role-relevant columns and labels. Hide irrelevant columns and
  repeated normal-state badges. Put long history and diagnostics behind a
  deliberate action, without hiding the reason a task cannot proceed.
- Align left header labels with cell content; align numeric labels with values'
  right edge. Shared sort controls must not add a second inset. Place sort icons
  inward from the alignment edge, and preserve alignment for wrapped labels and
  both active sort directions. Compare badges by their outer edge.
- Keep row actions compact. An inline editing form must not grow a table column
  and move every other value. Use an overlay/detail view for larger editing
  tasks. Opening and closing it should preserve row geometry and context.
- Base responsive changes on the space available after navigation and sidebars,
  not just the viewport. Dense tables may scroll where appropriate, but the
  primary task must remain discoverable and reachable. A compact row/card view
  is often better when scrolling would hide Review or Actions.
- Overlays need a title, a visible close action, sensible initial focus, Escape
  behavior and focus restoration. Keep background controls inert for modals.
  Check nested close events; a child dialog must not close its parent by accident.

For dense admin or staff workflows, load only the relevant reference:

- [tables-and-selectors.md](references/tables-and-selectors.md): deterministic
  pagination, remote selectors, selection scope and bulk outcomes.
- [forms-uploads-and-feedback.md](references/forms-uploads-and-feedback.md):
  structured field errors, durable upload outcomes and recovery.
- [permissions-audit-and-destructive-actions.md](references/permissions-audit-and-destructive-actions.md):
  action-level authorization, original-operator identity during impersonation,
  sensitivity-aware audit changes and correction previews.

An upload is complete when the saved asset is durable and readable. Impersonation
must stay visibly distinct and provide a direct return to the original operator.
These features are conditional on the product; do not add them merely to apply
this skill.

## Verify the workflow, then the rendered experience

Read [acceptance.md](references/acceptance.md) and select the cases relevant to
the change. Use realistic synthetic records: empty and populated states, long
names, multiple roles, mixed statuses and plausible numeric values. Fixtures
must obey the product's state model so screenshots do not normalize contradictions.

Run the rebuilt app and complete the affected journey. Inspect mobile, tablet
with navigation, desktop, loading/error and open-action states together. Measure
alignment or geometry when that is the reported defect. Do not stop at DOM
presence, HTTP 200, no overflow, or a screenshot of a closed control.

When useful and authorized, give an independent reviewer the task, brief and
rendered evidence, without telling them the expected verdict. Delegate a bounded
UX or test responsibility while doing other useful work. Skills and agents are
tools for finding problems, not proof of quality; retain their concrete findings.

Fix the demonstrated causes in one focused batch, rerun affected checks and
stop when the acceptance criteria are met. Do not add layers or hundreds of
implementation-mirroring tests to compensate for missing user-journey evidence.

## Preserve decisions and report honestly

Record requirement changes, rejected assumptions, source-of-truth locations and
verification limits where future agents can find them. Keep dates and superseded
decisions; do not relabel a proposal or a past failure as implemented success.

Maintain the project's lessons record alongside meaningful corrections. When a
demonstrated failure reveals a reusable gap in this skill, refine the relevant
rule or acceptance check in the same change. Keep product-specific choices in
project documentation, preserve dated evidence, and merge overlapping guidance
instead of accumulating a new checklist for every incident.

If push/deployment is authorized, complete the tests, push, deploy and public
verification without asking again. The skill itself grants no production access
or deployment permission. Preserve operator flags and credentials, verify the
actual schema when relevant, and keep a workable rollback. A UI release does not
authorize testing deletion, sending messages or making payments on real users.

Report implementation, local tests, deployment, live read-only checks and any
real provider transaction separately. Name only material untested areas. Do not
claim complete accessibility, performance or whole-site consistency from a
bounded check.
