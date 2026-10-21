# Frontend development: a reusable starting point

For new frontends and substantial existing-app UI work, use the globally installed
`build-usable-apps` skill. It now connects visual-reference research with the
existing workflow, recovery and browser-verification guidance.

- [Skill entrypoint](../custom/skills/build-usable-apps/SKILL.md)
- [Design workflow and acceptance gate](../custom/skills/build-usable-apps/references/frontend-design-workflow.md)
- [Provider catalog and reel provenance](../custom/skills/build-usable-apps/references/frontend-reference-catalog.md)
- [Anti Slop quality checks and integration](ANTISLOP.md): six upstream skills for
  targeted UI, copy, accessibility, responsive-layout and comment review.

Start with `ai-setup search "frontend-design-workflow"`, read the skill, then inspect the
target app's own design documentation and rendered UI. Existing apps retain their
useful tokens and components; new apps establish a design contract and one
representative screen before expanding. Marketing sites, business dashboards and
video editors need different density, navigation and motion choices.

The catalog links the original providers. The global setup now selects UI UX Pro
Max as a local reference skill; it does not install Refero MCP, Motion or 21st.dev
into every project. Paid live research is optional. Globally installed design and
animation skills are selected by task; application libraries belong in the
application that needs them.

## Reviewed additions — 19 October 2026

The user requested stronger design/motion skills and specialist roles. Three
independent research agents reviewed visual/product design, motion/native guidance
and role definitions using original provider sources. Search covered the skills.sh
catalog/CLI, official provider repositories and documentation; this is a bounded
review, not an exhaustive search of the internet or a UI quality benchmark.

| Selection | Added capability / decision | Pinned source and license |
| --- | --- | --- |
| `ui-ux-pro-max` | Add local searchable palettes, typography, interaction and stack guidance; keep scripts, data and references together. Heuristic recommendations need product-specific review. | [NextLevelBuilder](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/56ea9cf174ed86786187daa9de0e6247cb0747e4), MIT |
| `frontend-design` | Add a lightweight subject-specific direction and self-critique pass. Overlaps existing tools; use as an alternative, not another mandatory stage. | [Anthropic](https://github.com/anthropics/skills/tree/33375500bcea98d610eb30ce10ac4e59b89c390d/skills/frontend-design), directory Apache-2.0 |
| `gsap-core`, `gsap-react` | Add official animation/lifecycle guidance for GSAP work. No GSAP runtime dependency is installed. | [GreenSock](https://github.com/greensock/gsap-skills/tree/aed9cfd3277740755f6bfc1155c7aa645403b760), MIT skills; runtime has its own license |
| `expo-design-system`, `expo-native-ui` | Add token-drift audits and platform-specific native patterns. Match SDK versions; do not install the whole plugin, hooks or hosted MCP. | [Expo](https://github.com/expo/skills/tree/7ddc1f5796996e5c7efe2fc3fa9168eb24e8dac1/plugins/expo/skills), MIT |
| Brand Guardian, Visual Storyteller | Add brand/voice coherence and narrative/art-direction review. Existing UI Designer, UX and finish-gate roles still own their respective checks. | [Agency Agents](https://github.com/msitarzewski/agency-agents/tree/647c8baa42b6842afb4a97bf2c0950d45ba88e8b/design), MIT |
| Separate Impeccable modules | Reject duplication: installed unified skill already includes the relevant refinement commands. Newer browser-helper update deferred; requires separate executable review/PoC. | [Impeccable](https://github.com/pbakaus/impeccable) |
| Full Motion AI kit / Sleek / Interface Craft mirrors | Defer optional hosted/paid tooling; reject mirrors without established redistribution rights. Not required for these installs. | [Motion](https://motion.dev/docs/ai-kit-context), [Sleek](https://sleek.design/agents.md), [Interface Craft](https://www.interfacecraft.dev/) |
| Whimsy Injector / broad Design Engineering bundle | Defer: overlap and conflicting recipes; installed motion skills are preferable for implementation. | [Agency Agents](https://github.com/msitarzewski/agency-agents), [AgentsORG](https://github.com/AgentsORG/design-engineering) |

The two Agency files were inspected at the newer provider head and hash-checked
against the existing pinned revision: identical content, so no unrelated role
upgrade is necessary. Provider licenses are preserved in source caches and skill
folders. The only Pro Max packaging adaptation rewrites its plugin-relative
script path to the global skill location; no paid CLI or package is necessary.

Read the workflow's **Select additional specialists** section before applying
these providers. It records conflicting instructions, the GSAP callback cleanup
correction, Expo version/build/feedback boundaries and agent evidence limits.
The skills require no new paid account. Normal model usage, optional asset services
and future application runtime choices remain separate costs and decisions.

Local verification on macOS passed for six skills and two roles: pinned-source
and supporting-file comparisons, retained licenses, six Claude links, parsed Codex
role adapters and provider discovery through `ai-setup search`. An independent
reviewer confirmed those bounded checks. The local Pro Max CLI returned relevant
pricing, reduced-motion and hover guidance; the broad native touch query returned
generic Pressable advice, so a narrower `touch target size --domain ux` retry was
used and returned platform-specific target sizes. Results remain recommendations,
not measured UX improvements.

The normal `skills,agents` entrypoint installed the selected additions. Its first
scoped manifest lacked unrelated provider metadata required by whole-home
verification; the retry retained the full metadata and narrowed only selectors.
Whole-home verification then reported pre-existing edited global rules/docs and
instruction blocks. Those were preserved, not reset or marked PASS. An isolated
home installation of the same selections passed **16 managed-path checks** through
the normal entrypoint. The existing Build Usable Apps routing skill was refreshed
alone through the same installer methods and its two managed fingerprints passed.

Evidence: ignored `.ai-local/one-off/design-skill-install/` logs, search results,
scoped manifest and routing refresh helper. Manifest JSON, scoped diff whitespace,
central policy and active commit guard checks passed. No app UI quality benchmark,
Linux/Windows installation, paid provider trial or new-role model execution was
performed. Active clients may need a new session to reload their skill/role catalog.
The current checkout has unrelated edits; additions are local, not a Git publication
or an update to other machines. Base revision: `50cd10a002b7eb7e5479f4f500ca19d7b350b5c2`.

## Logo Design and local context tools

Added from the two subsequently reviewed reels: [Logo Design provider](https://github.com/kaankiziltug/logo-design-skill/tree/0ecf52e9a4b3ac92b714f7cc6e3148ab8c774134)
and [Context Mode provider](https://github.com/mksglu/context-mode). Reel provenance:
[first reel](https://www.facebook.com/share/r/1Di3e7JqzF/) and
[second reel](https://www.facebook.com/share/r/1Fw883EbsJ/). The provider repositories,
not the videos' promotional claims, are the implementation authority.

`logo-design` is a globally discovered provider skill for briefs, concept comparison,
geometric SVG marks, optical checks, favicon/app-icon variants and delivery sheets.
Use it when a project needs an identity or logo audit; preserve approved branding.
It complements `brandkit`'s raster brand presentations and the existing Brand
Guardian/Visual Storyteller roles. It does not replace the app's UI design workflow.

The complete provider skill, scripts, references and catalog are fetched at the
manifest commit and linked to both clients. Its MIT license and separate trademark
notice travel with the installed skill. The included third-party logo collection
is for reference, not permission to reuse brand marks or claim legal clearance.
Keep original project logos, chosen concepts and design decisions in that app.

SVG auditing, SVG variants and HTML sheets need only Python. PNG/ICO export needs
one existing renderer: Chrome/Chromium, Inkscape, rsvg-convert, CairoSVG or macOS
Quick Look. The installer does not add all of them. Run the provider's
`scripts/render_png.py --help` and check available backends before promising
raster delivery. On Windows invoke scripts with `python`/`py -3`, using the
absolute skill path, rather than assuming `python3` is a working alias.
The audit's zero exit code means the SVG parsed; inspect its findings for FAILs
and WARNs and visually review the 16 px/reversed/one-colour test sheet.

For example: “Use $logo-design to propose three original SVG marks for this app,
preserving its brand direction; show small-size and monochrome comparisons.”
Do not create an app-local copy of the skill or install a paid image provider.

[Context Mode](CONTEXT_MODE.md) is a default local MCP alongside this skill. It
helps with large test logs/specifications; it does not generate logos or sync
project discussions. Its guide documents scope, installation and live checks.

### Verification of these two additions

On 19 October 2026, isolated macOS ARM64 and Ubuntu 24.04 ARM64 container
installations passed repeat-install checks, SVG audit/variant/HTML generation,
both client MCP registrations, code execution, large-file reduction, index/search and second-project
separation. The Linux run used the actual `install.sh` entrypoint. Unit tests:
144 run, 140 passed, four existing platform-dependent skips. Native Windows x64
is implemented and covered by the new CI matrix but has not run on a Windows host
in this session. Debian was not run separately from Ubuntu.

The initial direct-server test exposed upstream fallback to inherited `PWD`:
a second project could retrieve the first test entry. `context_mode_server.mjs`
now binds the server to the MCP process cwd before loading the untouched provider;
the same two-project regression passed. The CLI does not implement `--version`,
so verification checks pinned package metadata, `--help` and real MCP behavior.

Current-user installation completed both components. Its aggregate verification
reported pre-existing edited global rules/docs/instruction blocks, which were
preserved. Scoped provider checks are separate from that unresolved whole-home
drift. Logs are in ignored `.work/contextmode-review/`, with maintained smoke checks
in `tests/check_design_context.py`. Changes are local/unpublished; other machines
are not updated. Installation does not establish improved visual taste or model
quality without a project-specific design acceptance gate.

## Distribution and discovery

The existing `custom` installer component copies the complete skill folder,
including its references. `rules` carries the task-selection instruction and
onboarding guide; `docs` carries this navigation page and the canonical skill
references in its documentation bundle. These components are used by the shared
Python installer behind both launchers:

```bash
# macOS / Ubuntu / Debian: from the updated ai_setup checkout
bash install.sh install --only custom,rules,docs
```

```powershell
# Native Windows: from the updated ai_setup checkout
.\install.ps1 -Only 'custom,rules,docs'
```

No new per-OS runtime is needed for Markdown guidance. Other machines still need
the published revision and their normal authorized update; this document is not
a claim that every machine or active agent session has already refreshed.
The installer preserves conflicting locally edited files for review.

Codex discovers `~/.agents/skills/build-usable-apps`; Claude uses its global skill
link. Restart a client if its skill catalog is stale. No app-local skill copies or
automatic application changes are needed. A direct invocation is:

> Use $build-usable-apps and its frontend design workflow. Inspect this app first,
> choose relevant references, define or preserve its design system, and verify
> the implemented screen and user journey in a browser.

## Shared knowledge

Git is canonical. The reviewed pointer in `HINDSIGHT_LIBRARY.json` identifies this
guide by source hash; Hindsight supports semantic discovery, not code installation
or guaranteed recall. Agent Wiki holds a sanitized proposal with source paths,
revision/hash and evidence limits. Neither store should receive raw videos,
private project assets, transcripts or credentials.

Review status: guidance derived from inspected references, not a controlled UI
quality benchmark. Record each app's actual design decisions and acceptance
evidence in that app. Capture new generic failure lessons in the existing skill.
