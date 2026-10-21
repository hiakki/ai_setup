# Browser and component quality

Reuse the app's Playwright Test installation and supported browser. Do not
download a second browser stack merely because a profiling CLI is available.
App changes need the app owner's authorization. The centrally maintained
`templates/quality/browser.spec.ts` provides functional, axe and screenshot
checks; adapt it to real controls and keep it in the application's test suite.
The installed templates are in `~/.local/share/ai-setup/quality/templates/quality`.
Use app-local pinned `@playwright/test` and `@axe-core/playwright` dependencies.

Establish a reviewed screenshot baseline for each relevant OS/browser/font set.
Test representative desktop/mobile widths, keyboard focus and reduced motion.
An axe pass covers detectable rules, not full WCAG compliance. Do not update
baselines automatically to hide failures. Keep failing screenshots, traces and
the original command/exit code in app-owned or ignored evidence.

## React

Read `vercel-react-best-practices` for waterfalls, rendering and bundle issues;
`vercel-composition-patterns` for component API composition. Use the app's actual
React/Next version and profile a representative route before claiming a speedup.
These complement the design contract and accessibility checks.

## Chrome performance, only when needed

`chrome-devtools --help` exposes the pinned provider CLI. Start an isolated Chrome
session only for an authorized target; inspect the current CLI help for the
session/profile and trace options. Disable usage statistics and CrUX queries
(`--no-usage-statistics`, `--no-performance-crux` on supported start/server flags).
Never connect a personal signed-in browser or expose remote debugging publicly.
Stop only the session you created after recording the trace. The installer does
not register a second always-on browser MCP or start/download Chrome.

Compare the same route, data, viewport, cache state and throttling. Preserve raw
traces. A Lighthouse score or one synthetic trace is not field performance.
See [provider documentation](https://github.com/ChromeDevTools/chrome-devtools-mcp).

## Storybook MCP, conditional on an application's Storybook

This is an app-owned server, not a single global endpoint. Use the central
`templates/quality/storybook-mcp.md` recipe for Storybook 10.6.2. Do not install
Storybook or change an app without its owner's approval. Confirm supported
framework capabilities, enable the component manifest where supported, and test
discovery against that app's running Storybook before registering its local MCP
in the active client. Stop/reconfigure it with the app's normal workflow.
Do not register an invented port globally or use the archived standalone repo.

Sources: [Storybook AI](https://storybook.js.org/docs/ai),
[Playwright axe integration](https://playwright.dev/docs/accessibility-testing),
[visual comparisons](https://playwright.dev/docs/test-snapshots).
