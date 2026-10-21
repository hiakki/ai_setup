---
name: openrig-team
description: Coordinate a persistent Claude/Codex specialist team through OpenRig with one lead conversation. Use for explicit team requests or sustained cross-discipline work; ordinary small changes can stay in the current agent.
---

# Shared specialist teams

Read `~/.local/share/ai-setup/openrig-team/README.md` for supported commands and
platform limits. Use `ai-team roles` for the actual installed roster.

Before launch, identify the authorised project path, read its instructions and
current docs, search `ai-setup` and relevant Hindsight/Wiki lessons, and select
only useful roles. Preparing a team is not authorization to implement an app,
deploy, scan, publish, restart services or access another project. Preserve all
existing approvals and ownership boundaries. Reuse global skills and MCPs.

`ai-team prepare --project PATH` creates a private, project-specific roster.
`ai-team start --project PATH` starts its lead only. Use the installed client's
configured model; do not invent model names, silently change providers or spend
on another inference service. Use `--runtime claude-code` when that is the user's
chosen client, otherwise the default is Codex. Missing login is a real blocker.
`ai-team activate --project PATH --roles backend,qa` starts selected specialists.
Read the start/activate result and `ai-team status` before assigning work.

The lead is the user's central contact. Convert each requirement into a bounded
brief with project path/revision, approved scope, acceptance criteria and
dependencies. Consult specialists during planning, then return material unresolved
choices to the user. Implementation follows the user's existing scope approval.
Give work a named owner through `env OPENRIG_HOST_SELECTED=local rig queue`; use
`env OPENRIG_HOST_SELECTED=local rig send` for direct questions. Pin local routing
on all coordination commands, including inside seats from a reused daemon.
The exact CLI syntax is available with `rig queue --help` and `rig send --help`.
Messages are not tracked assignments. Every specialist reports evidence and
unresolved issues back to the lead. The lead reconciles conflicts and supplies
one consolidated answer; do not require the user to shuttle between terminals.

Keep no more than three specialists actively working by default; increase only
when the task benefits and resources permit. Do not broadcast every prompt to
the whole roster. Give each discussion a decision or stop condition; escalate
after two unresolved exchanges. Agree file ownership before parallel edits.
Use one checkout unless concurrent conflicting work requires an isolated one;
do not create forks/worktrees merely because a role exists.

Use an independent reviewer for substantial changes. Completion requires the
actual acceptance checks, not agent consensus. Mark blocked/skipped checks
honestly. Each specialist must read its delivered skills and current project
instructions. Frontend/design work includes the applicable Figma and browser
workflow; tool unavailability must be reported, not silently skipped.

Keep project evidence with its owning app; promote only reviewed generic lessons
to the central library and the existing user's Wiki proposal area. No automatic
conversation uploads. Role definitions are reusable; project conversations and
credentials are separate. Instructions and role labels are not OS isolation.
