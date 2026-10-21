---
name: development-quality
description: Evaluate coding agents or skills with real artifacts and independent checks; choose React performance/composition guidance, AST rules, API contract testing, browser accessibility/visual regression, Chrome performance profiling or explicit output compression. Use for improving development speed or output quality, setting up regression gates, and selecting these shared tools for an existing or new project.
---

# Development quality

Start from the application's current docs and existing checks. Read only the
reference matching the task. Installation is availability, not permission to run
scans, spend on model calls, start services or modify other applications.

| Task | Read / use |
|---|---|
| Evaluate a coding agent, skill or instruction change | [Agent evaluation](references/agent-evaluation.md), `promptfoo-evals`, `promptfoo-provider-setup` |
| React/Next performance or reusable components | `vercel-react-best-practices`, `vercel-composition-patterns`; verify framework version in Context7 |
| Accessible, responsive or visual UI checks | [Browser quality](references/browser-quality.md), `build-usable-apps` and the existing Playwright runner |
| Syntax patterns and safe structural rewrites | [Structural and API checks](references/structural-api.md), `ast-grep` |
| API contract/property/stateful checks | [Structural and API checks](references/structural-api.md), `schemathesis` |
| Chrome performance investigation or Storybook component context | [Browser quality](references/browser-quality.md) |
| Excessive CLI output | [Output handling](references/output-handling.md), explicit `rtk` or existing Context Mode |

Use Codebase Memory first for code relationships; ast-grep is for syntax matching.
Do not load every design skill or add another memory/browser service. Keep tests,
screenshots and API schemas with their application; generic lessons belong in the
central library. Preserve exact commands, exit codes and raw failures. Separate
static checks, synthetic fixtures, real app checks and measured improvement.

The `quality` installer component provides these CLIs globally on supported
macOS/Linux and native Windows x64. Run a tool's `--help` before unfamiliar usage.
On Windows, use `.cmd` launchers for Promptfoo, ast-grep, Schemathesis and Chrome
DevTools; RTK is `rtk.exe`. No WSL is required. Missing tools: use the central
installer's `--only quality`, not per-project copies or floating `npx @latest`.
