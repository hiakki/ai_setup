# Shared design ownership

Use for every web or native UI change. The default is to preserve the approved
design and compose existing controls, not design each screen independently.
Use the project's existing contract; a small fix needs a few updated lines,
not another design-system document or dependency.

## Before editing

Record the relevant owner chain with the task:

`approved contract → semantic token → shared control → consumer version → wrapper → screen`

Read actual source and rendered behavior. Matching package versions or importing
a shared component does not establish that wrappers preserve its states.

Identify which layer owns each requested change. Search for an existing button,
action row, field, selector, dialog or navigation item before writing one. For a
new app, establish the minimal shared controls on one representative screen
before expanding. If no appropriate control exists, say so and choose its owner;
do not claim to reuse an export that does not exist.

## What belongs where

| Concern | Owner and acceptance |
| --- | --- |
| Brand colors, type, spacing scale, radius and elevation | Semantic tokens. Use roles such as primary action, surface and destructive action; no per-screen brand palettes. |
| Repeated controls and interaction states | Shared component or semantic variant. Preserve pressed, focus, disabled, loading, selected and open behavior where applicable. |
| Screen composition and business behavior | Screen/feature. Different role journeys and layouts are intentional; do not force them into one giant component. |
| Platform behavior | Appropriate native/web primitive behind the relevant API. Shared branding does not require identical widgets. |
| Exceptional appearance | Narrow documented exception with reason, owning path, affected consumers and evidence. Existing explicit approval remains valid; do not invent an approval round. |

Do not override a shared button's background, shadow, radius or state styles in
a screen merely to match one screenshot. Fix the owning token/component for a
repeated problem, or add the smallest meaningful semantic variant. A wrapper
must forward required state and accessibility behavior; it must not turn a
shared interactive control into static text or a static style object.

Local grids, image crops, scrims, icon geometry and meaningful status colors can
be legitimate. A raw color, StyleSheet, Pressable or CSS declaration is an audit
candidate, not proof of a defect. Do not remove native semantics or keyboard
focus to satisfy a cosmetic preference.

## Prevention that can be checked

For a confirmed recurring fault, use existing app lint, type, component or
regression tests to express the specific invariant. Examples include forbidden
obsolete control imports, consumer pin drift, unsupported wrapper overrides or
lost disabled/pressed state through a defined wrapper API. Avoid a new universal
scanner unless the project has a concrete need and an agreed policy.

Demonstrate both a violating example that fails and a valid layout, semantic
status or native-control example that passes. Resolve aliases, spreads and
composition before treating a source match as a failure. Do not count keyword
matches or the presence of a shared import as proof of UI consistency.

Record the real check command and where it runs. A proposed check is not active
enforcement. A local Git hook may be bypassed; a required check only covers its
configured scope. Respect existing CI/CD ownership and approval boundaries;
do not change a pipeline merely because this guidance mentions checks.

## Before sign-off

1. Verify one representative rendered consumer before spreading the change.
2. Check affected consumers on their actual surfaces and relevant rest, pressed,
   focus, disabled/loading, selected/open and enlarged-text states. Include
   role-relevant destinations and actions below the first viewport.
3. For a shared-control change or repeated correction, have an independent
   reviewer inspect the brief and real state captures before seeing the proposed
   verdict. If no reviewer is available, record that gap; do not invent sign-off.
4. Record owner revision, consumer adoption, environment and remaining gaps.
   Separate source-only risks from rendered defects and deliberate differences.

Use [acceptance.md](acceptance.md) for detailed interaction and evidence checks.
Never call the whole app visually approved from component tests or one screen.

## Cross-machine limits

The global rule and this skill are distributed by ai_setup's existing `rules`
and `custom` components for Claude Code and Codex on macOS, Linux and Windows.
Publication, installation and agent use are separate facts. Verify the installed
rule and complete skill references after an authorized update; preserve personal
edits and check the reported source revision. Existing agent sessions may need
to reload instructions. Other clients need their own supported integration.

This is maintained guidance plus app-owned verification, not model training,
a filesystem prohibition, an automatic deployment gate or a guarantee that
every future agent will follow instructions. Report those limits honestly.
