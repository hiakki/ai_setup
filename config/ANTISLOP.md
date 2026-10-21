# Anti Slop quality checks

Anti Slop is already installed centrally for Claude and Codex. For substantive UI
work read the global `antislop` skill with `build-usable-apps`, then select the
relevant modules: `antislop-ui` for visual composition, `antislop-copywriting` for
product/marketing copy, `antislop-human` for accessibility, and
`antislop-layoutmobile` for responsive layouts. Use `antislop-code` only for a
requested code-comment review, not as authority to change program behavior.
Small fixes need only their relevant checks; do not load all six for every task.

This is the ai_setup integration policy and takes precedence over the provider's
installation and workflow defaults. Skip its first-run installation wizard and
project-local skill/rule copies. Resolve the core as the installed
`antislop/SKILL.md`; run supporting scripts relative to their installed skill
folder (Claude-specific variables are not available in every client).

Use `during` as the integration default while doing authorized work. Respect an
explicit session mode or an existing upstream settings preference, including
`ask`; never overwrite that preference. A review-only request stays read-only
regardless of mode. Do not ask again for scope/assets already authorized. Keep
audit evidence in the app's existing documentation or ignored AI scratch area,
not a new reusable local library. Report only relevant checks with actual evidence;
do not manufacture PASS results for the provider's delivery checklist.

Preserve approved branding, working controls, meaningful comments, licenses and
tool directives. Treat stylistic bans as contextual guidance, not permission to
restyle every app. Never invent statistics, testimonials or production data.
Verify keyboard/focus, responsive content, contrast and reduced motion in the
actual UI when relevant. The bundled contrast script checks solid color pairs,
not complete accessibility or image/gradient backgrounds. No additional MCP,
CLI, npm dependency or background service is required. See `docs/ANTISLOP.md` in
the central library for provenance, operation and verification limits.
