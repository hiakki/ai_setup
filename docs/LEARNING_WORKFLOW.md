# Keep current app docs local and engineering experience shared

Search terms: learning workflow, learning capture, failed attempts, migrations,
superseded decisions, current architecture, crons, CI/CD, retrospective, new app.

An application explains **what exists now**. ai_setup explains **what we learned
getting there** and points to useful implementations. Use the
[project catalog](PROJECT_CATALOG.md) for current sources and the
[case catalog](case-studies/README.md) for reviewed experience.

## Maintain the application's current operating picture

Extend existing owner docs rather than generating a parallel documentation tree.
When a task changes architecture or operations, update the relevant section in
the same work. Use a small README section for a small app; larger systems can
link separately owned references. Identify source revision, last review date,
owner and any implementation-versus-deployment difference.

| Area, when applicable | What the app should explain |
| --- | --- |
| Architecture | Responsibilities, runtime processes, dependencies, important request/event journeys, data/write authority and trust boundaries; proposals clearly separated |
| Crons and background work | Purpose, owner, scheduler/config source, timezone and DST policy, enabled/paused status, concurrency/overlap control, retries, missed-run handling, idempotency and success/failure inspection; observation date for live status |
| CI/CD | Workflow locations, triggers and branch/tag policy, checks, build/artifact identity, release/promotion, credential ownership without values, deployment target, operator gates and rollback |
| State and operations | Databases/storage, migrations, backups/restores, monitoring, dependency failures and recovery entry points |
| Evidence | What was proposed, implemented, tested, deployed and exercised through a real workflow; unresolved gaps |

Mark not applicable or unknown explicitly. Documentation does not authorize
creating missing cron jobs, pipelines or infrastructure. A configured schedule
does not prove a job ran; a green pipeline does not prove the customer journey.
Retain original ADRs and dated release/incident evidence with the app even after
their approach is superseded. Update the current overview so old instructions
cannot masquerade as the active design.

## Capture meaningful experience before closing the task

Do this after a significant correction, failed approach, architectural switch,
migration, incident or release that teaches something reusable. Routine edits
need no ceremonial retrospective or new case.

1. **Reconcile app docs.** Record the resulting current state; keep original
   observations, decisions and test/release artifacts with their owner.
2. **Find the existing lesson.** Search by project and failure mechanism; use
   `ai-setup library` to locate the authoring checkout. Read the matching skill
   and case before adding another file.
3. **Preserve the reasoning.** Amend the case using the fields below. Retain
   failed and superseded approaches when they explain a later decision;
   distinguish an observed symptom from a demonstrated cause.
4. **Generalize once.** Put an enduring decision rule into the existing skill
   when genuinely missing. Keep historical detail in the linked case. Update
   the project catalog if source paths changed.
5. **Validate and distribute.** Check source identity, privacy, evidence labels,
   links and actual search results. Apply local global-copy updates within the
   authorized scope. Commit/push and updates on other machines require their
   normal authorization; capture is not automatic publication.

If the central checkout is unavailable or outside the allowed edit scope, record
the pending promotion and owner-source pointer in the app's normal handoff and
report it as pending. Do not create a local reusable skill copy or claim sync.
Private reusable material requires an authorized private destination.

## Minimum useful learning entry

Use these fields inside the existing case; they need not become separate files:

- **Problem and context:** general trigger and material constraints; omit private
  product details, customer facts and raw conversation text.
- **Approach tried:** what was attempted versus merely considered.
- **Observed result:** what passed or failed, under which conditions. Preserve
  failed verification attempts rather than reporting only eventual success.
- **Reason for switching:** demonstrated cause or explicit hypothesis, tradeoff,
  user constraint or evidence that changed the decision.
- **Replacement and status:** adopted, partial, superseded, rejected, deferred
  or proposed; link successors and retain why an older choice once made sense.
- **Verification and limits:** document/source review, simulated/unit checks,
  sandbox/provider tests, deployment and actual end-to-end result separately.
- **Reuse:** when to adopt, adapt or avoid it; the target-specific acceptance gate.
- **Provenance:** origin, owner-relative paths, dates, source revision and
  dirty/non-Git content hash where needed. Source identity is not runtime identity.

The [DelX case](case-studies/delx-durable-execution.md), for example, preserves
why retrying an uncertain request could duplicate a mutation, what durable
intent changed, and that tests used a fake provider. The
[NarrateAI case](case-studies/narrateai-automation-and-evidence.md) retains a partial
repair and later repeated failure instead of claiming unattended reliability.

## Start a new app from evidence

1. Search by the target's topic and relevant origins. Read matching cases,
   including failures, and their applicable skill references.
2. Use the project catalog to locate a useful current implementation. Within
   authorized access, inspect owner docs and relevant source/configuration;
   check graph coverage for structural claims and current provider contracts
   where material. Do not read every sibling repository by default.
3. Record **adopt / adapt / reject**, target fit, evidence limits and a concrete
   verification gate in the new app's docs. Reuse principles without silently
   copying private code, business rules, credentials or infrastructure.
4. Implement the authorized scope and verify this app's actual journey.
   Report which historical lessons and current sources informed it.

## What this setup enforces

Use the [coverage report and local delta checker](LEARNING_COVERAGE.md) during a
collection pass. Keep observed-file changes separate from semantic review status;
do not declare all learning captured merely because two inventories match.

Installed Claude/Codex instructions and skills require this workflow. The Git
guard rejects project-local skill libraries; it cannot infer that a prose lesson
is complete or force an agent to capture every discussion. There is no background
transcript collector, sibling-repository crawler, scheduled sync or model
retraining. Search proves discovery, not correct reuse. Existing cross-platform
docs/rules/custom/hub installers distribute this guidance.
