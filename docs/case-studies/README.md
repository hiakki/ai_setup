# Cross-project engineering lessons

Use these cases to make recommendations concrete without copying an application's
private documentation into the shared library. Search by the origin **and** topic,
read the case and its linked skill, then explain what to **adopt, adapt or reject**
for the target and how to verify it. Original project decisions and release
records remain authoritative. These cases are maintained AI learning, not model
training or automatic access to sibling repositories and past conversations.

For current implementations, follow the [project catalog](../PROJECT_CATALOG.md).
After a meaningful correction, failure, migration or switch, use the
[learning-capture workflow](../LEARNING_WORKFLOW.md) to amend the relevant case
without losing the earlier result or reason for changing direction.

## Case catalog

| Origin and case | Find it with `ai-setup search` | Useful for | Evidence ceiling |
| --- | --- | --- | --- |
| [Panyora](panyora-service-extraction.md) | `"panyora cicd"` | Service extraction, centralized builds, artifact promotion, security and QA | Recorded execution, implementation and proposals distinguished; no blanket financial or new-topology validation |
| [Elvique](elvique-operational-workflows.md) | `"elvique observability"` | Shared business authority, operational UX, proxy failures and telemetry | Requirements plus a recorded proxy repair/local telemetry test; production app telemetry activation not established |
| [Servinoza](servinoza-workflow-recovery.md) | `"servinoza recovery"` | Approval versus hold removal, resumable agreements, responsive admin work and state-specific tests | Consolidated corrections with attributed release checks and proposals; no fresh live financial test |
| [NarrateAI](narrateai-automation-and-evidence.md) | `"narrateai automation"` | Unattended agent workflows, asset identity, provider errors, publishing intent and analytics | Failed real-app trial plus partial repair and offline checks; unattended reliability not established |
| [bulkBuyer](bulkbuyer-data-provenance.md) | `"bulkbuyer provenance"` | Data freshness, scoring semantics, point-in-time evidence, caches and dependent reports | Dated access incident and documented controls; predictive performance remains unvalidated |
| [DelX](delx-durable-execution.md) | `"delx reconciliation"` | Durable intent, uncertain requests, cancellation races and recovery ownership | Source audit and fake-provider regressions; no real external execution verified |
| [card-savvy-india](card-savvy-calculation-and-comparison.md) | `"card-savvy comparison"` | Signed imports, unknown values, score versus money, mobile comparison context | Reproduced calculation findings remained open; separate UI checks do not close them |
| [logging_cost and istio_issues](infrastructure-cost-and-drift.md) | `"logging_cost drift"` | Workload-shaped cost estimates, configuration drift and limits of incident hypotheses | Attributed retrospective/drift reports; no new savings, rollout or causal verification |
| [musician-metronome-macos](metronome-native-audio-evidence.md) | `"metronome audio"` | Platform adapters, native build integration and audible acceptance | Repair notes and test instructions; no completed native/listening result established |

Choose by failure mechanism, not only by similar business type. For example,
DelX's uncertain-request lesson can inform a provisioning job, and NarrateAI's
missing-versus-zero distinction can inform an operational dashboard. Such reuse
still requires the target's actual contract and verification.

## What was checked in the 28 September review

The later [learning coverage audit](../LEARNING_COVERAGE.md) extends this initial
pass with additional sources, cases, a local delta checker and explicit remaining
gaps. The disposition table below describes the earlier pass, not final clearance
of every document in those directories.

The local `contrib` inventory covered 40 other project directories besides
ai_setup and the already reviewed Panyora workspace. It found visible Markdown,
MDX or RST files in 34. Git-ignored material and common generated/runtime folders
were excluded. This was a **documentation discovery pass with selected detailed
reviews**, not a full code, security or conversation audit of every project.

| Disposition | Projects | What this means |
| --- | --- | --- |
| Detailed source records represented in the catalog | Elvique, Servinoza_in, NarrateAI, bulkBuyer, DelX, card-savvy-india | Selected incident, correction, reliability and QA documents read directly; exact sources and evidence limits are in each case. Elvique's existing case is reused. |
| Consolidated under the current project case | Servinoza | Earlier entrypoint screened; this pass uses Servinoza_in's later correction record, not a duplicate case or claim to have reviewed every older decision. |
| Infrastructure material screened, not promoted as established guidance | istio_issues, logging_cost | Audit/tuning and cost-analysis records include private operational context. Their causal and savings claims need stronger outcome evidence before becoming shared prescriptions. No cluster identifiers, bills or configuration payloads copied. |
| Personal material excluded from detailed harvesting | career-ops | Document paths inventoried; personal applications, profiles and dossiers are not public-library learning. No claim to have read hundreds of generated records. |
| Provider-owned documentation retained upstream | outline | Entrypoint/inventory screened; do not vendor an upstream project's manuals as original lessons. |
| Entrypoints screened; no separate case promoted in this pass | E-Commerce-Platform, GhumaggerSnap, IoTSwitch, ParleyAI, ScoutTraderAI, TicTacToe, book-keeping, curl_commands, free_videos, frontend_example, graphical-web, msDeploy, musician-metronome, musician-metronome-macos, newProject1, ollama_web_app, pdfEditor, spendAnalyser, tax_calculator, testing, ui-automation-agent, windos-app, workflow-canvas-web-app-react | Selected setup/feature/plan entrypoints do not establish a verified failure-and-repair case. Nested records and code may contain further lessons; they were not exhaustively audited. Old model comparisons and proposed safeguards are not current benchmarks or verified outcomes. |
| No matching visible documentation in this inventory | Food-Order-Project-06, HardQuestions, QReports, debugging_auto_ssl, n8n-workflows, scripts | Search-scope result only. It says nothing about ignored files, code, other formats or prior conversations. |

Graph coverage was checked for the selected sources. Changed metadata and excluded
documentation were resolved by direct reads; no application code was structurally
audited for this synthesis. Historical reported checks are explicitly attributed
to their records and were not rerun here.

## Keep the library useful

Update the existing case when a later record changes its conclusion. Keep the
general trigger, failed assumption, action, verification and remaining limits.
Retain source path, revision or working-tree hash, and review date; a dirty file
must not be represented as committed content. Use authorized local source access
for later verification; a provenance path is not permission to fetch private data.

Put enduring decision rules in the relevant existing skill and detailed cases here.
Do not create a new skill for every project or duplicate the same case in several
topic documents. Keep private formulas, customer/account data, credentials, raw
conversations and full runbooks with their owner. Current policy, provider behavior
and product terms require fresh authoritative research before a recommendation.

The [engineering playbook](../REUSABLE_ENGINEERING_PLAYBOOK.md) routes to maintained
skills. Install/update distributes this catalog through the existing docs component
on macOS, Linux and native Windows; no application checkout is a runtime dependency.
Other machines need their normal authorized update. Finding a case proves retrieval,
not that an agent read it, applied it correctly or produced a better design.
