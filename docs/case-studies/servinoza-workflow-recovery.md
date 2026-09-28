# Servinoza: state transitions, recovery and rendered QA

Reviewed: 28 September 2026. Search terms: Servinoza, Servinoza_in, onboarding,
admin UX, recovery, approval, hold, payment, tables, responsive QA, cancellation.

This sanitized case derives from the application's consolidated correction
record. It preserves failures and decision criteria, not the application's
commercial terms, required identity documents or operating procedures. Original
decisions and release evidence remain in the source project. No application or
provider flow was rerun for the original document review. The dated extraction
addendum below has its own observed runtime evidence and limits.

## Decisions worth transferring

| Trigger in the source record | Reusable action | Verification and limits |
| --- | --- | --- |
| An action labelled Restore called approval, trapping an incomplete held account behind approval prerequisites. | Define removing a hold separately from granting approval. Match the label, server transition and next available task. | Exercise recovery with incomplete evidence, not only successful approval. The source records the correction; this review does not establish its current deployment. |
| Accepting a visit also committed a price before inspection. | Separate initial estimate, accepted visit, proposed scope/price, agreement and verified payment. Preserve earlier facts and resume at the saved stage. | Test refresh, stale tabs, failed/pending payment and attempted edits to paid scope. Source records a correction; real money movement needs separate evidence. |
| A paid screen still said to wait for payment because two controls received different relation/context data. | Derive messages and enabled actions from the same authoritative context. | Check both the correct message and absence of contradictory guidance in the paid state. A resting screenshot or typecheck missed this failure. |
| A table had no page overflow but its primary actions were hidden beside a tablet sidebar. Header cell edges aligned while padded text did not. | Base responsive decisions on available container width; measure visible task controls and rendered text, not just rectangles. | Inspect sorting, wrapped labels, hover padding, focus, modal open/close and compact layouts. The source records local and live table checks, with populated held/flagged cases only in local fixtures. |
| Pending search responses replaced current input; failed actions hid errors behind a modal. | Preserve the current draft across asynchronous responses and put failures within the active interaction. | Use delayed responses and rejected mutations; verify focus handoff and a usable retry. A successful fast response cannot cover these states. |
| Cancellation and replacing a professional were represented by ambiguous actions. | Separate ending the task from changing its future assignee. Snapshot accepted terms and retain the historical owner of work and receipts. | Test stale previews, repeat replacements and both before/after-payment paths. The consolidated record describes design and linked implementation evidence; do not infer every path was verified live. |
| An email-first recovery proposal coexisted with an implemented flow whose first durable save happened later. | Describe the actual persistence boundary. Distinguish sending a code, verifying it, creating an account and saving a draft. | Leave and return at each real boundary. A proposal is not an existing capability; SMTP acceptance is not inbox delivery. |

These patterns apply to many approval, booking and administration systems. They
do not mandate this project's roles, payment provider, document collection or
review policy. Simplify presentation only after preserving the underlying facts.

## Use the maintained guidance

- [Build usable apps](../../custom/skills/build-usable-apps/SKILL.md): state models,
  resumable tasks and browser acceptance.
- [Auditable business workflows](../../custom/skills/auditable-business-workflows/SKILL.md):
  accepted terms, corrections, historical ownership and financial isolation.

Search `ai-setup search "servinoza recovery"`. For the target, record which
lesson to adopt, adapt or reject and the test that would establish the outcome.
Keep the target's decisions in its own repository.

## Source and evidence boundaries

Source: `Servinoza_in/docs/architecture/UX_LESSONS_AND_REUSABLE_SKILL.md`.
The record was consolidated on 25 September and includes later dated amendments.
It distinguishes earlier attributed reports from directly checked table release
evidence. A later correction does not make an earlier passing review comprehensive.

Baseline repository HEAD: `b05d2212f9e5041c8617e132c2b94b71a54ef8dc`.
The source was **modified in the working tree**, so HEAD is not its content identity.
Reviewed SHA-256: `10e263f3c1ba188164a2230f57ad5b15ec002915078b580aa050f688018e2b1c`.
Graph coverage reported changed metadata; the source was read directly in full.

This is a document synthesis, not a fresh implementation, security, accessibility
or financial audit. No private media, account records or original conversations
are included. Follow linked owner records in an authorized checkout for current
release status; this case remains usable without that private access.

## 28 September addendum: staged extraction and journal ingestion

**Problem and approach tried.** Service extraction initially advanced toward image
and CI machinery before the separated ordinary processes were proven. The operator
selected a staged sequence: ordinary services, local image builds, Compose, then
automation. Existing later-stage source was retained as deferred work. Application
docs distinguish deployed owners from the still-required compatibility host.

**Why the replacement matters.** Clean detached service builds exposed undeclared
parent dependencies; live probes separated restricted database grants, user
journeys and worker ownership. A normal API deployment did not replace its
background scheduler. The migration remains partial; this is not a completed
microservice, independent-database or CI/CD claim.

**Failed monitoring check.** A candidate collector configuration validated, loaded
and reported ready with mounted host journals. Synthetic traces reached the trace
backend, but journal line counters remained zero and no matching logs appeared.
The candidate was rolled back and replaced with explicit journal-directory
selection while retaining exact worker filters and the existing curated pipeline.
Both synthetic log records then correlated with their traces. Other monitoring
services stayed unchanged. This supports the directory-selection repair in the
tested Alloy v1.19.2 deployment; it does not establish a universal container cause.

**Reuse and limits.** Follow the target operator's stage order; use isolated
artifacts, preserve transaction authority and verify the actual public journey.
Before worker handover, prove both scheduler fencing and telemetry ingestion.
Collector readiness, mounted files and valid syntax are insufficient. A synthetic
probe must not invoke financial work and is not evidence of normal scheduled
batch success, delivery, settlement or provider recovery.

**Provenance and successor pointers.** Current application migration evidence is
owned by `servinoza-docs/MIGRATION_EXECUTION.md` (revision `083e5b9` at this
observation); collector attempt, rollback and replacement evidence is in
`servinoza-ops/docs/WORKER_HANDOVER_REVIEW.md` (revision `4bfd74c`). Older parent
records above remain historical evidence. Current releases may advance; resolve
those owners before reuse. No customer records, infrastructure credentials or raw
release logs are included here.

The generic rules are maintained in
[staged extraction](../../custom/skills/service-architecture-and-extraction/references/staged-extraction-to-cicd.md)
and [observability checks](../../custom/skills/reliable-web-app-operations/references/observability-and-incidents.md).
