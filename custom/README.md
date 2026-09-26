# Local additions

Browse the [custom skill catalog](skills/README.md) for directory names, purposes,
requirements and installation instructions. Each skill has its own portable folder.

These are the exceptions to fetching provider material. They came from the user's existing local setup or were authored here for shared workflows, not cached from an upstream collection.

- `ai-model-comparison`: local guidance created on 2026-09-26 after correcting inherited quantization scores. Requires configuration-matched evidence, separate reference results and unranked unknowns. It contains methodology, not cached provider benchmarks or model weights.

- `laya-decisions`: explicitly confirmed by the user as created locally on 2026-09-23. Preserves the helper, synthetic fixture and offline regression tests. Adds environment-only endpoint/token configuration for another machine. No credential file is included.
- `hyperdx-ui-regression-memory` and `sre-incident-investigation`: local operational guidance without a recorded upstream source. The HyperDX project path now refers to the authorized project rather than one Mac's path; delegation refers to an available authorized specialist.
- `build-usable-apps`: moved from Servinoza_in on 2026-09-25, including workflow patterns, acceptance checks and UI metadata. Portable workflow guidance; Servinoza decisions and release evidence remain in that project.
- `social-rights-review`: moved from NarrateAI on 2026-09-25. Its trigger now covers media projects generally. Supporting policy references retain their original research date and revalidation requirement; clip-specific findings remain in NarrateAI's review documents.
- `india-card-research`: moved from card-savvy-india on 2026-09-25. Reusable Indian card research and arithmetic guidance; application instructions and its specialist agent remain local.
- `auditable-business-workflows`: moved from Elvique on 2026-09-25 with references for source facts/calculations, hierarchy/status/corrections and financial snapshots/demo isolation.
- `reliable-web-app-operations`: moved from Elvique on 2026-09-25 with deployment/environment, provider-delivery and observability references. Distinct from the existing SRE incident-investigation workflow.
- `hermes-workflows`: local integration guidance created on 2026-09-26. Explains bounded invocation, shared-skill discovery and promotion of learned material. Hermes's own code and bundled skills are downloaded from NousResearch; they are not copied here.

Elvique's `operational-admin-ux` was merged into `build-usable-apps`, preserving its three detailed admin references. The [engineering playbook](../docs/REUSABLE_ENGINEERING_PLAYBOOK.md) records the merge rationale and reusable lessons.

These ten custom folders are maintained sources. The `custom` component installs complete folders to `~/.agents/skills/` and links them for Claude. Modify the source here, then reinstall within the authorized scope; do not maintain divergent copies in consuming projects. See [global skill migration](../docs/GLOBAL_SKILLS.md) for routing and provider provenance.

The formerly unattributed frontend/security/DevTools instructions were matched to original commits in [Addy Osmani's agent-skills](https://github.com/addyosmani/agent-skills). Incident response was matched to [Anthropic's knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins). They are fetched through the manifest, including their reference assets; their contents are not stored under `custom/`.

The browser-devtools skill still requires an independently configured Chrome DevTools MCP; Playwright is installed separately. The HyperDX guidance needs the actual project and its evidence documents. Availability of an instruction does not establish availability of its remote tools.

All 32 attributed Agency specialist definitions are fetched from the Agency Agents provider repository. They are not stored here.
