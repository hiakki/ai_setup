# Code intelligence tool routing

The global setup provides complementary tools. Use one first and add another only when it resolves a concrete evidence gap.

| Need | First choice | Why |
| --- | --- | --- |
| Symbols, callers, routes, impact and coverage | Codebase Memory MCP | Persistent local structural graph with evidence-coverage checks |
| Fast source context, repository map or fallback call trace | Graft | Compact current-code context and source packs |
| Smallest complete implementation or focused review | Ponytail | Implementation discipline; it is not another index |
| One graph spanning code, ADRs/docs, schemas/config, PDFs or Office files | Graphify | Mixed-artifact relationships and extracted/inferred provenance |
| Literal/config value or unsupported file | Direct read or `rg` | Precise and cheaper than building another graph |

## Installed behavior

Ponytail is fetched from `dietrichgebert/ponytail` at the revision in `manifest.json`. Its six skills are globally discoverable by Claude and Codex. Its lifecycle hooks are not installed because global rules already govern ordinary sessions.

Graphify is fetched from `Graphify-Labs/graphify` and installed in an isolated, versioned environment with the provider's `pdf`, `office`, `sql` and `terraform` extras. The provider-generated generic Agent Skills package is published globally. The MCP extra, always-on search guards, per-project installer and Cloud service are not enabled.

Run Graphify from the project root only when the investigation needs mixed artifacts:

```bash
graphify --help
graphify extract .
graphify query "How does the documented deployment flow connect to the implementation?"
```

Graphify writes `graphify-out/` by default. Keep it local and ignored. Review source scope before adding documents: code parsing is local, while semantic document/media extraction can use the active assistant or an explicitly configured backend. Do not configure a separate model or upload private documents without task authorization.

Do not install Graphify's MCP server or guards alongside the default stack. Codebase Memory remains the first structural tool, Graft remains the source-context fallback, and Graphify is invoked only for its mixed-artifact advantage.
