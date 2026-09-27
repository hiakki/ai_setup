---
name: api-docs-governance
description: Design, audit, or implement API documentation ownership, service catalogs, contract publication, and AI navigation across repositories. Use for central API portals, documentation drift, architecture references, and reliable cross-repo change context; not ordinary endpoint implementation or copy editing.
---

# API Documentation Governance

Make an API or workflow discoverable without losing its owner, version, business meaning or verification evidence. Fit the solution to the actual project; a monolith does not need extra repositories to use this skill.

For actual service decomposition or runtime extraction, use `service-architecture-and-extraction` when available. This skill owns the documentation/contract part of that work; improving docs alone does not require reorganizing runtime code.

## Establish the task and existing authority

- Separate research/proposal, bounded audit and implementation. Research does not authorize repository creation, source moves, portal publication, deployment, new subscriptions or tool installation.
- Inspect the existing documentation index, contracts, route registration, package exports, compatibility/deployment records and applicable repository instructions. Preserve user changes and working consumers.
- Use configured code-discovery tools according to project rules. Verify graph freshness/coverage before relying on absence; use exact source where coverage is missing. Documentation/configuration inspection does not require building a code graph for an unrelated workspace.
- Distinguish intended, implemented and observed deployed behavior. A release record with a timestamp can be historical; `main`, a version label or an HTTP 200 does not establish the live contract. Mark unknown states explicitly.

## Choose ownership before tools

Prefer a central discovery experience composed from owner-maintained contracts and docs when that fits independent service teams. Compare alternatives fairly: centrally designed contracts can be appropriate; a gateway may genuinely own a transformed external API. Do not assume one layout is a formal standard or require a dedicated docs repo.

Keep domain contracts with their authority, gateway routing/composition with the gateway owner, operational procedures with ops and database recovery with its operator. Schema migrations may have a different source owner from the database runtime. Every document needs a purpose and owner; no generic shared/documents dumping ground.

For architecture, publication and adoption decisions, read [ownership-and-publication.md](references/ownership-and-publication.md). It includes an adaptable catalog, CI gates and release-state distinctions.

## Build evidence useful to people and agents

- Connect each operation/workflow to owner, source revision, consumers, relevant invariants and executable checks. Provide readable docs plus machine-readable contracts and stable links.
- Document network exposure, authentication, authorization and documentation visibility separately. OpenAPI security declarations and hidden docs do not enforce tenant or field access.
- Describe side effects, retries, idempotency, concurrency, units, errors and recovery where relevant. Generated types do not imply runtime validation; schema conformance does not prove business correctness.
- Keep personal AI configuration, graph caches and private notes local/ignored under the user's policy. Team-neutral technical docs can be versioned. Reuse existing agent roles and local adapters instead of duplicating global instructions per project.
- Keep context small: start page → owner/contract/workflow → exact source/tests. MCP and llms.txt are optional discovery mechanisms, not correctness or ingestion guarantees.

For bounded delegation and reader testing, read [agent-review-and-evaluation.md](references/agent-review-and-evaluation.md). Use agents only when authorized and useful; run the same checks locally when delegation is unavailable. Do not create permanent agent registrations just to run a review.

## Research and delivery

For current market/tool claims, consult primary sources and distinguish standards, documented platform patterns, emerging proposals and your recommendation. Read [sources.md](references/sources.md) for starting points; recheck current versions/capabilities rather than treating the research date as permanent truth.

Start with a thin ownership index and one meaningful workflow pilot. Add generated publication and compatibility automation before expanding coverage. Choose a supported specification subset only after testing the exact pinned tools; avoid assuming the latest format is universally supported. Preserve existing contract packages during migration.

For proposals, provide an ownership map, authority/provenance rules, focused diagrams, alternatives/tradeoffs and phased acceptance gates as warranted by scope; a small documentation improvement may need only a short plan. For implementation, verify the changed workflow, generated output, links and access boundaries. For an audit, state the bounded scope and gaps. Separate document validation, source inspection, mocked tests, runtime tests and live verification. Never label planned infrastructure or unrun checks as completed.
