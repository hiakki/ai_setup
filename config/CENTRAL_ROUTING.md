# Central shared AI setup

Follow the Global rules above for ownership, case research, learning capture and
application approval. This block adds operational details without repeating them.

- Before shared work: `ai-setup search "TOPIC"`, read relevant results, then
  `ai-setup library` for the canonical checkout. For current remote content use
  `--refresh`; report a failed refresh and label local evidence as stale. Never
  create a project-local substitute or claim freshness after failure.
- Author reusable skills/roles/lessons centrally; app docs stay with their app.
  This supersedes older all-docs-central rules. Private reusable material needs
  an authorized private source; secrets never belong in the public library.
  Preserve team instructions and keep personal configuration/caches ignored.
- Research cases by topic/reference project. `ai-setup search "project catalog"`
  locates owner-maintained current docs; `ai-setup search "learning workflow"`
  locates capture guidance. Read those sources within authorized access before
  adopting or recording lessons. Preserve superseded reasoning and source evidence.
  Search is literal; it does not fetch sibling repos or past conversations. A
  central update does not refresh app checkouts or guarantee recall/model learning.
- Before committing: `ai-setup check-project --project PATH`. A Git guard is not
  a filesystem sandbox; report enforcement gaps. See
  `{{REFERENCE}}/CENTRAL_LIBRARY.md` for policy and exceptions.
- Inspect `ai-setup status`. Shared references are at `{{DOCS}}`.
  Use `ai-setup sync --dry-run` to preview a full machine refresh and `ai-setup sync`
  when authorised to apply it; this includes new defaults and previously selected
  optional components. `ai-setup update` refreshes shared content only. Check the
  reported revision, local edits and actual target-tool behavior before claiming sync.
  Export a reviewed local skill edit with `ai-setup contribute SKILL --checkout
  PATH_TO_AI_SETUP`; provider skills remain upstream-owned. Export/update does
  not authorize commits or publication. `ai-setup update` runs only when requested;
  no scheduled updates, transcript capture or automatic publication are enabled.
