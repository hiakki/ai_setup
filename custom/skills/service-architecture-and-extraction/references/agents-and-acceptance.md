# Specialist work and acceptance gates

These briefs reuse available roles. They do not require permanent agent registrations or authorize extra tools. For small work, apply the relevant review locally. For substantial authorized parallel work, use independently useful tasks, not several agents rediscovering the same code.

## Shared handoff

Give each worker: objective, approved directory/behavior scope, applicable instructions, current/proposed state, exact owned files, source revisions, discovered symbols/call chains, graph generation and coverage/gaps if applicable, tests and known unresolved questions. State that others may be editing; preserve their changes and do not revert unrelated work. Do not assume a child has MCP access. Never pass credentials or unnecessary customer data.

Keep dependent edits sequential. A service contract and its consumer need a common agreed interface before both implement changes. Assign one coordinator to the cross-repo compatibility and release decision.

## Bounded role briefs

- **Software Architect:** assess domain/transaction boundaries and alternatives; identify what should remain together and transitional coupling. Provide current/target diagrams with data/provider dependencies. Do not assume more repos improve scalability.
- **API Platform Engineer:** verify interface compatibility, gateway routing/forwarding, trust assumptions, private/public separation and consumer impact. Read exact handlers and affected boundary tests.
- **Application Security Engineer:** review the scoped actor/tenant/service credential matrix, secret/PII distribution and bypass paths. Report evidence and residual risk; no broad scans or security guarantees.
- **DevOps/SRE:** verify artifact/config ownership, rollout order, actual process/env/schema, worker handover, public-path checks and rollback. Do not restart, deploy or delete beyond existing authorization.
- **Database specialist:** verify privileges, migration ordering/locks, schema drift, connection budget, backup isolation and disposable restore evidence. Treat restoration separately from code rollback.
- **Browser/QA reviewer:** exercise the actual actor workflow, persistence, restricted behavior and relevant layout/interaction/print states. Report console/network errors and distinguish screenshots from successful operations.
- **Independent finish reviewer:** inspect the final diff and evidence against the requested outcome. Identify untested boundaries, unowned resources, hidden parent dependencies and overstated readiness claims.

Ask a research agent for primary-source verification only when current external facts or alternatives matter. Do not upload private source to an external research/scanning provider by default.

## Acceptance prompts for plans or skills

Use fresh-context scenarios without supplying the intended answer:

1. A small monolith asks for better parallel work but has one tightly coupled financial transaction. Propose a proportionate boundary and validation plan.
2. Six independent repos run on one VM and database. Explain which changes can deploy separately and what data/network isolation is actually achieved.
3. An extracted login handler passes normal tests but lost a pre-parser size cap; a streamed request has no content length. Identify evidence and a useful regression path.
4. A public gateway route succeeds, but a second tenant can request another tenant's resource directly. Explain what the passing route test did and did not establish.
5. A code rollback is requested after new customer orders were written. Evaluate a proposed restore of yesterday's dump.
6. The old parent directory has been renamed; HTTP health is green, but uploads, a billing timer and migration configuration have not been checked. Evaluate cleanup readiness.
7. A platform payment sandbox succeeds; a separate merchant's integration and settlement are unverified. State what can be claimed and the next required evidence.

Evaluate correct authority, scoped actions, source/evidence use, recovery behavior, preserved data and explicit unknowns. Do not reward checklist size or confidence. Scenario review validates reasoning only; actual service releases require the appropriate runtime evidence.
