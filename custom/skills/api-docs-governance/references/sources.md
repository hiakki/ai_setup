# Primary-source starting points

Research provenance: distilled from a multi-repository API/documentation review on 27 September 2026. These are starting points for verification, not permanent claims about current versions, market adoption or tool compatibility. Reopen relevant official documentation when making a current recommendation. No project credentials, repository inventory or deployment details are embedded in this skill.

| Source | What it supports | Boundary |
|---|---|---|
| [OpenAPI specification](https://spec.openapis.org/oas/latest.html) | HTTP API description format and semantics | Does not dictate repository layout or enforce authorization |
| [Backstage catalog](https://backstage.io/docs/features/software-catalog/) | Central discovery with metadata maintained alongside code | Platform pattern, not a requirement to install Backstage |
| [Catalog descriptors](https://backstage.io/docs/features/software-catalog/descriptor-format/) | Ownership, lifecycle, component/API relationships | Declared relationships are not observed calls |
| [TechDocs architecture](https://backstage.io/docs/features/techdocs/architecture/) | Publishing source-owned docs into a common experience | Hosting and operational responsibilities remain |
| [Redocly bundle](https://redocly.com/docs/cli/commands/bundle) | Resolving a description's references into an artifact | Bundling is not joining independent APIs |
| [Redocly internal filtering](https://redocly.com/docs/cli/decorators/remove-x-internal) | Producing selected projections | Unmarked nodes are not removed; public eligibility needs validation |
| [oasdiff support notes](https://raw.githubusercontent.com/oasdiff/oasdiff/main/docs/OPENAPI-31.md) | Current parser and format support caveats | Recheck the exact pinned tool release |
| [Schemathesis](https://schemathesis.readthedocs.io/en/stable/quick-start/) | Schema-driven implementation checks | Does not replace business or authorization tests |
| [Pact applicability](https://docs.pact.io/getting_started/what_is_pact_good_for) | Consumer/provider contract testing and limits | Not complete provider functional or payment verification |
| [AWS ADR guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html) | Decisions, consequences and supersession | Adapt the process to team size and task |
| [C4 diagrams](https://c4model.com/diagrams) | Architecture views at useful levels | Do not require every level for every task |
| [Diátaxis](https://diataxis.fr/) | Tutorials, task guides, reference and explanation | Organization guidance, not mandatory directory layout |
| [AGENTS.md](https://agents.md/) | Open coding-agent instruction convention | Verify actual client discovery; no automatic sibling-context guarantee |
| [Claude memory](https://code.claude.com/docs/en/memory) | Scoped instructions and loading behavior | Version/configuration-dependent, not enforcement |
| [MCP resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) | Versioned protocol for resource discovery and reads | This URL pins a protocol version; it does not establish the latest revision or guarantee retrieval |
| [llms.txt](https://llmstxt.org/) | Proposed index and Markdown discovery convention | Proposal, not authorization or universal ingestion |
| [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Focused context and retrieval on demand | Vendor guidance, not a quantified accuracy guarantee |
| [Agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Tasks, repeated trials, traces and outcome evaluation | Requires grounded expected answers and measured results |

Keep research conclusions attributed and dated. Prefer a concrete compatibility pilot over popularity claims. A new standard or tool capability does not itself justify adding infrastructure.
