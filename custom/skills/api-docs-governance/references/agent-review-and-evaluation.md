# Reusable specialist review and AI evaluation

Use these bounded briefs with available roles; they are task templates, not permanent agent definitions. Avoid delegation for a small single-file edit. Do not require agent availability to complete the work.

## Delegation packet

Give reviewers the user objective and scope, applicable instructions, permitted side effects, current/proposed distinctions, exact source paths/revisions, observed facts, coverage limits and unresolved questions. Where graph tools are used, include project/generation, queries and pagination, relevant symbols/call chains, coverage results and source fallbacks. Do not assume a child inherits graph access or private credentials.

For independent reader testing, provide only the document and realistic questions rather than the expected answers. A review can run while the main agent validates links or inspects another independent scope. Give workers exclusive file ownership if edits are delegated; tell them other agents may be editing and not to revert others' work.

## API platform research brief

> Within the supplied project scope, compare contract ownership and central publication approaches. Use primary sources for current tool claims. Distinguish formal specifications from vendor patterns and recommendations. Evaluate consumer compatibility, schema authority, gateway composition, artifact provenance, deployment states and documentation exposure. Return precise citations, limitations and the smallest suitable adoption path. No installs, repository creation, publication, private-source uploads or runtime changes.

## Developer tooling / AI context brief

> Assess how a fresh agent can identify an operation's owner, version, consumers, business invariants and checks from the supplied evidence. Evaluate instructions, catalog navigation, source links and retrieval. Do not assume sibling repositories enter context or that a graph has complete coverage. Separate local personal configuration from shared technical docs. Propose measurable reader tasks; do not invent productivity scores or guaranteed understanding. Read-only within the assigned scope.

## Independent reader brief

> Read the supplied document as an engineer unfamiliar with the project. Answer: Where is the canonical schema edited? Who owns routing, releases and database recovery? How can I identify the deployed version? What is proposed versus implemented? Where should a cross-service change and its tests go? What is the smallest next step? Cite the document, state unknowns and flag contradictions or hidden prerequisites. Do not edit files or use outside project knowledge to fill gaps.

## Evaluation method

For a substantial workflow change, compare before/after with fixed source revisions, the same model/tool setup and repeated fresh-context attempts. Use human-reviewed expected results and retain traces. Evaluate source selection, citation correctness, owner/consumer identification, stale-version errors, unsupported assertions, correct checks, outcome correctness and retrieval cost. A confident final explanation is not evidence of a successful change.

Select realistic cases, including a negative case:

- Find where an approval or permission rule is enforced and the relevant negative test.
- Identify consumers affected by changing a response field.
- Distinguish provider transport from domain ledger/fulfillment authority.
- Detect disagreement between a historical manifest and current docs; report deployed state unknown when observations are absent.
- Explain migration-source ownership versus backup/recovery ownership.
- Detect a missing pinned artifact without silently falling back to a branch.
- Retrieve only authorized docs, including raw specifications and search exports.

Small skill changes can be forward-tested with synthetic, self-contained scenarios without running services. Significant implementation changes need actual checks of the changed flow. Report scenario review, static validation, mocked tests and runtime verification separately.
