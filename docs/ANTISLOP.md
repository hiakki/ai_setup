# Anti Slop: shared quality checks

The [reel](https://www.facebook.com/share/r/1C7jf7NLPv/) points to
[miqdadbadjuber/anti-slop](https://github.com/miqdadbadjuber/anti-slop).
Public reel metadata identified the provider; provider source, not promotional
claims, informed this integration. Reviewed 19 October 2026: upstream v3.2.21,
MIT, pinned commit `439a2ef5b9dd0ebe74e8113ff43f5928d0fe2a6a`.

It complements the existing design workflow with checks against generic UI,
unsupported claims, inaccessible interactions and weak mobile layouts. It is
guidance, not a measured improvement in model quality or an accessibility audit.

| Global skill | Use |
| --- | --- |
| `antislop` | Core purpose, evidence and delivery checks |
| `antislop-ui` | Composition and working interface controls |
| `antislop-copywriting` | Specific, supported product/marketing copy |
| `antislop-human` | Contrast, keyboard, focus and perceivable states |
| `antislop-layoutmobile` | Reflow, overflow, navigation and touch targets |
| `antislop-code` | Useful code comments; preserve directives and rationale |

## Installation and use

Both `install.sh` and native Windows `install.ps1` install these through their
existing default `skills` component. Provider folders are fetched directly from
GitHub into the user's source cache, installed under `~/.agents/skills`, and linked
into Claude's skills directory. Codex discovers the shared skills directory.
Supporting Python scripts and MIT license are retained. Five companion skills'
core references are rewritten to `../antislop/SKILL.md`; provider content is not
vendored in this repository. No separate npm CLI, MCP registration or service is
installed. Optional provider contrast MCP code is present but not enabled.

`config/ANTISLOP.md` is merged into both clients' global instructions when the
provider is installed. This skips the upstream project-copy wizard, applies
checks during authorized work by default, and respects explicit/saved mode
preferences. It creates no preference file. Existing `ask` preferences still ask;
review-only tasks stay read-only. Existing app branding and scope take precedence
over stylistic prescriptions. The Build Usable Apps workflow selects these skills
by task, without loading all six for each edit.

Examples: "Use Anti Slop to review this dashboard; do not edit" or "Build this
screen using our design system and the Anti Slop accessibility/mobile checks."
Resolve the installed `antislop-human/contrast-check.py` path and run it with
`python3` on macOS/Linux or `python` on Windows. Solid-color calculations do not
verify gradients, images, keyboard behavior or the complete accessibility standard.

Existing and new projects share this user-level setup; they need no local copies.
Start a new Claude/Codex session to refresh discovery. Other machines need this
revision published and their normal authorized installer/update run first. Nothing
here automatically changes an existing app, guarantees skill invocation, or pushes
unpublished changes to another computer.

## Verification

On 19 October 2026, macOS ARM64 fresh-home install and repeat install passed all
12 managed skill/link checks plus global instruction blocks. The six skills were
also installed for the actual local user and discovered through `ai-setup search`.
Pinned source, every installed provider file, rewritten core references, licenses
and Claude links were compared. The nine-pair contrast self-test passed, as did
explicit black/white PASS and grey/white FAIL cases. The frontend routing skill
was refreshed separately and its persisted installer fingerprints passed.

Ubuntu 24.04 ARM64 passed installation through the actual `install.sh`, repeat
installation and the same provider/contrast/state checks in an existing Docker
image. The first inline verification command had an unmatched parenthesis; the
corrected verification rerun passed. Installer regression suite: 12 tests,
11 passed and one Windows-only skip. The new routing regression was observed
failing before implementation and passing afterwards; it checks personal-rule
preservation, repeat installation and rejection of edited managed blocks.

Native Windows and separate Debian execution were not performed. The existing
macOS/Ubuntu/Windows CI matrix now includes Anti Slop through
`tests/check_design_context.py`; this is prepared CI, not a completed remote run.
App-specific visual quality and accessibility still require actual browser checks.

Whole-home verification continues to report pre-existing edited global rules,
shared docs and instruction blocks; these were preserved. A frontend-skill flag
during its concurrent refresh was followed by a fresh persisted-state check,
which passed. These bounded checks do not declare the entire installation clean.
Canonical changes are local/unpublished at base
`50cd10a002b7eb7e5479f4f500ca19d7b350b5c2`. No other machine has been updated.
