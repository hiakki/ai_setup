---
name: hyperdx-ui-regression-memory
description: Investigate recurring HyperDX UI interaction bugs and preserve verified component, embedding-context, and regression evidence in the project's persistent UI memory. Use for HyperDX dropdown, popover, field-picker, and related interaction regressions.
---

# HyperDX UI regression memory

Use the existing project knowledge graph for structural code discovery and the repository document below for observed behavior. A graph relationship does not establish browser behavior; a remembered fix does not establish the current deployment's behavior.

## Retrieve before diagnosing

Read `<authorized-hyperdx-project>/agent_docs/ui-interaction-memory.md` and relevant linked evidence. If it is missing, report that and create an evidence-based entry during the investigation; do not imply prior knowledge was retrieved. Follow the workspace's graph discovery and coverage instructions, checking current source whenever the graph is stale or a path is untracked.

Identify the actual source snapshot: checkout path, branch, commit, relevant uncommitted changes, and deployed image/version when available. Do not silently test a dirty checkout as a proxy for the deployed build. Preserve unrelated work.

## Reproduce the interaction in its context

Capture the exact control, page, role, steps, and outside-click destination. For dropdown dismissal, include the surrounding expanded log row or details area when present, parent event handlers that stop bubbling, nested controls, and portals. Test outside targets inside and outside the embedding container. A standalone component fixture can miss a parent that intercepts events.

Establish a failing regression before changing the responsible behavior where practical. Keep interactions inside the dropdown working: selecting, typing, reordering, removing fields, and interacting with a child portal must not accidentally dismiss its parent. Verify Escape and reopening when relevant. Use condition-based assertions and accessible selectors. Retain concise before/after evidence and the command needed to reproduce it.

When parallel work is useful, delegate a bounded context audit or regression review to an available UI review specialist, only when delegation is authorized. Pass source freshness, coverage gaps, exact ownership, and unresolved questions; do not duplicate edits.

## Record evidence without inflating it

Update the project memory with the observed symptom, root cause or unresolved hypothesis, component paths and embedding surfaces, regression test, artifact paths, source revision, and remaining gaps. Keep these levels distinct:

- **Static:** source and event-handler inspection only.
- **Unit/integration:** automated fixture behavior, with mocks and embedding context stated.
- **Browser:** the named real browser flow, local or remote, with exact build/context.
- **Deployed interaction:** the affected flow exercised on the deployed version. Healthy pods, HTTP 200, and a matching bundle are deployment evidence, not interaction verification.

Record failures and unresolved surfaces as well as successes. Do not extrapolate one passing fixture to all dropdowns or overwrite a prior failure with an untested assumption. Link a prior entry when new evidence changes its conclusion. Keep secrets, cookies, raw customer payloads, and tokens out of memory and artifacts.

This skill does not deploy, install another memory service, or authorize external writes. End with the actual verification level, remaining uncertainty, and links to the saved evidence.
