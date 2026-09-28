# Learning coverage and outstanding delta

Reviewed: 28 September 2026. Search terms: learning coverage, learning delta,
existing projects, new projects, contribution, unreviewed docs, missing lessons.

Existing and new projects using this user's refreshed Claude/Codex installation
can discover the library and receive its capture rules. That is instruction
availability, not guaranteed agent compliance or proof that every past discussion
has been captured. This audit must not be reported as “zero delta everywhere.”

## What this pass added

| Source area | Destination and disposition |
| --- | --- |
| logging_cost retrospective; istio_issues drift report | [Infrastructure cost/drift case](case-studies/infrastructure-cost-and-drift.md): capture measurement and configuration lessons; do not promote unverified savings, tuning or causality claims |
| musician-metronome-macos repair/test notes | [Native audio case](case-studies/metronome-native-audio-evidence.md): capture the missing integration/audible acceptance gate; no claim the repair passed |
| NarrateAI offline speech audition | [Existing case](case-studies/narrateai-automation-and-evidence.md#audio-experiment-follow-up): preserve controlled comparison, excess-silence repair, timing and subjective-quality limits |
| DelX pipeline, cross-engine and earlier profitability audits | [Existing case](case-studies/delx-durable-execution.md): cache identity/isolation, data boundaries, observed duration, double-counted evidence, supervision and history-versus-current state |
| bulkBuyer export and UI audits | [Existing case](case-studies/bulkbuyer-data-provenance.md): inspect actual archived output, matching denominator/label, unknown outcomes, exact-request retries and interaction state |
| Servinoza later mail adapter and auth-segregation records | [Existing case](case-studies/servinoza-workflow-recovery.md): explicit versioned test artifacts, uncertain acceptance identity, stream revocation and separate source/local/deployed security evidence |
| Elvique backup/recovery guide; Servinoza admin-workflow review | Existing operations and usable-app guidance already covers the reviewed backup/restore gates and return-path/bulk-limit lessons. Keep product commands, policies and original evidence in the apps; no duplicate case needed. |
| book-keeping troubleshooting, frontend_example notes, msDeploy deployment-guide excerpts | Screened, not promoted as verified incident outcomes. Generic guidance, file-size claims and hypothetical deployment procedures do not establish user-visible performance, diagnosis or a successful release. |

Each promoted case identifies exact source paths, revisions/hashes, scope and
verification limits. The source applications and providers were not rerun. For
unindexed source directories, direct document reads supplied evidence; no code
graph or live-runtime completeness is claimed.

## Inventory and access boundaries

A fresh Git-ignore-aware `rg` inventory found **759 visible Markdown/MDX/RST
files in 34 project directories**, excluding ai_setup, Panyora's previously
reviewed workspace and common generated/vendor folders. Relative to the earlier
inventory, one new path was found: the Servinoza mail-integration guide. Five
vendor Pod documents were removed from this discovery scope. These counts mean
files inventoried, not files semantically reviewed or lessons captured.

Detailed review remains selective. The [earlier project disposition table](case-studies/README.md#what-was-checked-in-the-28-september-review)
records all 40 other directories, including those with no matching visible docs.
Private career dossiers, upstream/vendor manuals, ignored runtime artifacts,
past chat histories, deleted Git history and remote-only repos are not harvested
into this public library. Personal record filenames and raw inventory stay local.

Remaining learning delta includes unreviewed sections/records in larger projects,
undocumented reasoning, later edits and inaccessible private/remote history.
For example, this pass did not exhaust every Servinoza decision/incident section,
DelX strategy experiment or Elvique product specification. Existing cases may
cover their general patterns; that is not evidence all unique lessons were found.
Promote additional material only after reading it and checking for duplication.

## Can projects follow and contribute?

- Global Claude/Codex instruction files include central discovery and capture
  rules. Existing projects need a client/session that loads them; new machines
  need the normal authorized installation/update.
- Project-local rules may impose a narrower edit boundary. Read them before
  central authoring; report pending promotion if the canonical checkout is outside
  the task's allowed scope. Do not edit installed skill copies as an alternative.
- Twenty top-level Git repositories were checked. Nineteen selected the global
  guard; NarrateAI selected `.githooks` instead. Its inspected pre-commit hook
  delegates to a Git-identity script; the hook itself has no central-policy
  invocation. Downstream script chaining and remote required checks were not
  audited; no local `.github` directory was present.
  Nested Panyora repositories were outside
  this hook audit. Non-Git directories have no commit gate.
- The guard checks placement of reusable skill libraries, not whether prose was
  learned or an agent followed the capture workflow. Hook bypasses and other
  clients remain separate enforcement limits. No app hooks were overwritten.

Use the [learning workflow](LEARNING_WORKFLOW.md) to consume and contribute:
search/read → inspect current owner evidence when needed → adopt/adapt/reject →
verify this app → update owner docs and the relevant central case/skill → publish
and refresh only when authorized. Record a meaningful no-new-lesson decision
without creating duplicate prose just to satisfy a checklist.

## Detect new file delta without claiming semantic completion

The bundled [local delta checker](tools/learning_delta.py) uses Python 3.11+ and
only the standard library. It hashes Markdown/MDX/RST files under an explicit
authorized root and reports added, changed and removed paths. It does not export
document contents, run source instructions, use the network or change Git/hooks.
Snapshots are observations, never reviewed/approved/captured marks.

From the canonical checkout, choose an existing ignored/private output directory:

```sh
python3 docs/tools/learning_delta.py --root /authorized/projects \
  --exclude ai_setup --exclude career-ops --exclude outline \
  --snapshot .work/learning-observed-1.json

python3 docs/tools/learning_delta.py --root /authorized/projects \
  --exclude ai_setup --exclude career-ops --exclude outline \
  --baseline .work/learning-observed-1.json
```

On Windows use `python` with the appropriate local paths. The installed helper
is under `~/.local/share/ai-setup/docs/docs/tools/learning_delta.py`. It ships via
the existing docs component, including native Windows; no service is installed.

Unlike the `rg` inventory above, this helper deliberately **does not interpret
Git ignore files**: it can detect ordinary ignored documentation. It excludes
hidden entries, symlinks/junctions and named dependency/build/output folders;
explicit `--exclude` paths restrict further. Its JSON reports the exact scope.
Exclude known downloaded-runtime and fixture trees explicitly (for this workspace,
`--exclude NarrateAI/data --exclude DelX/state` avoids dependency/test-state noise).
Use the same root and exclusions for comparison; mismatched scopes, malformed
baselines, read failures or a changing file fail instead of silently passing.
Existing snapshots are never overwritten. Keep path/hash snapshots private and
out of Git; they can reveal project and file names even without document content.

### Actual comparison check

The scoped helper scan covered 550 files after explicit runtime/private-source
exclusions. The installed helper later detected a concurrent edit to
`Servinoza_in/repos/servinoza-docs/MIGRATION_EXECUTION.md`. Its full text and Git
diff were read. Disposition: **already covered / current app state**. The existing
Servinoza case and extraction guidance cover staged rollout, actual schema/grants,
preserved operator settings and candidate-versus-active evidence. Changing service
revisions and journey results remain in the owner document; no duplicate case was
created. This is a concrete change-detection check, not clearance of all 550 files.

Reviewed owner HEAD: `083e5b9b697dd1cf99bcb55b819956831b8350b8`, with local edits;
document SHA-256: `ad87d5b0e93ae4ed8ffa3aa4e680f5650ccf82e4180332f9c6c169052a66c8d7`.
Later changes require another review. The original observation remains intact.

Retain the old snapshot and review each delta against existing cases. Record
captured, already covered, app-only, private, proposed or pending disposition with
source identity and destination. Only then create a separate next observation;
do not reset the inventory to conceal pending reviews. No changed files means
only no detected file changes in this scope, not zero outstanding learning.
