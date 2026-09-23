# Local additions

These are the exceptions to fetching provider material. They came from the user's existing local setup, not a cached upstream collection.

- `laya-decisions`: explicitly confirmed by the user as created locally on 2026-09-23. Preserves the helper, synthetic fixture and offline regression tests. Adds environment-only endpoint/token configuration for another machine. No credential file is included.
- `hyperdx-ui-regression-memory` and `sre-incident-investigation`: local operational guidance without a recorded upstream source. The HyperDX project path now refers to the authorized project rather than one Mac's path; delegation refers to an available authorized specialist.

The formerly unattributed frontend/security/DevTools instructions were matched to original commits in [Addy Osmani's agent-skills](https://github.com/addyosmani/agent-skills). Incident response was matched to [Anthropic's knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins). They are fetched through the manifest, including their reference assets; their contents are not stored under `custom/`.

The browser-devtools skill still requires an independently configured Chrome DevTools MCP; Playwright is installed separately. The HyperDX guidance needs the actual project and its evidence documents. Availability of an instruction does not establish availability of its remote tools.

All 32 attributed Agency specialist definitions are fetched from the Agency Agents provider repository. They are not stored here.
