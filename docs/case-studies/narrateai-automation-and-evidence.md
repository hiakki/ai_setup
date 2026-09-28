# NarrateAI: automation trials, asset identity and publishing evidence

Reviewed: 28 September 2026. Search terms: NarrateAI, video, agentic automation,
unattended jobs, provider refusal, retry, asset identity, publishing, rights,
analytics, missing counters, zero views.

This case summarizes recorded application trials and implementation guidance.
It contains no private draft URLs, media, account settings or publishing tokens.
No generation, provider call or publication was performed for this review.

## A repaired demo did not prove unattended operation

The 20 September trial submitted two fresh drafts through the signed-in app.
Neither produced a final video unattended. A patch let one retry pass its first
attachment failure while reusing existing assets, but a later provider refusal
stopped it. The second fresh draft reproduced attachment recognition failure
on patched code. The record explicitly says the attachment issue was not fully
fixed. Its passing test suite did not validate the whole provider sequence. [S1]

This is a diagnostic sample, not an estimated long-term failure rate. A previous
completed demo required intervention; it cannot be counted as an unattended run.

| Source lesson | Apply elsewhere | Evidence boundary |
| --- | --- | --- |
| A thumbnail token was useful only when bound to the expected canonical gallery asset. | Persist canonical asset identity; reject conflicting explicit identifiers. Resume from validated saved outputs rather than regenerate everything. | S1 records a regression and successful reuse, but a remaining attachment failure. Do not treat one repaired URL/token pattern as universal. |
| A provider's terminal refusal appeared as a generic application error. | Preserve actionable provider reasons. Separate transient failures, terminal refusals and unknown outcomes; bound retries. | S1 records the refusal, not a capacity or credit failure. Resource exhaustion was not established. |
| An image fallback would change a promised full-animation deliverable. | Define any permitted fallback before rollout and visibly report the reduced result. | S1 lists this as remaining work. Silent degradation is not successful completion. |
| Approval and Publish were separate states tied to an exact output. | Bind external-action intent to reviewed media, source, title and destination; invalidate stale jobs after regeneration. A production build mode alone must not authorize publishing. | S2/S3 describe implementation and offline checks; this review did not publish or independently test the gate. |
| Source metadata could report a license or partner claim without establishing reuse permission. | Preserve unknown evidence; assess exact assets and applicable rights separately from editorial quality and account monetization eligibility. | S2 records a metadata model, not a legal clearance service. Use current official policy when assessing a new use. |
| Fetch failures could look like zero audience response. | Preserve real zeros, unknown values, per-platform fetch times and denominators separately. Retain prior counters on errors and disclose their age. | S3 describes reporting changes. Lifetime counts are not matched-age outcomes, retention or revenue; no audience improvement was measured. |

For a new agent workflow, measure completed fresh runs, interventions, time,
provider cost and output quality through the real app. Add restart/outage tests
and a sustained trial when unattended operation is the proposed outcome. Do not
schedule or spend merely because an offline test passed.

## Reuse

Search `ai-setup search "narrateai automation"` or
`ai-setup search "narrateai analytics"`. Read
[reliable operations](../../custom/skills/reliable-web-app-operations/SKILL.md)
for recovery and provider evidence, and
[social rights review](../../custom/skills/social-rights-review/SKILL.md)
for a current asset-specific assessment. Adopt, adapt or reject each relevant
pattern against the target's actual provider and output contract.

## Audio experiment follow-up

A separate offline speech audition preserved identical spoken words and voice
identity across delivery variants, with loudness-normalized comparison copies
and original outputs retained. It reported actual synthesis and decodable audio,
but explicitly left subjective listening and pronunciation approval pending.
Warmed synthesis time, model loading, first-run initialization and normalization
were different measurements; the Mac result was not a production-VM benchmark.

The first directed pass combined model sentence-tail silence with added pauses,
creating excessive gaps. The recorded change trims only outer quiet padding
before applying the intended pause once; it preserves silence inside a spoken
beat. Later captions use actual segment timings, without claiming word alignment.
An experiment remained optional and did not switch the production provider.

Reuse the controlled comparison, timing decomposition and explicit rollout gate;
do not infer perceptual quality from finite samples or a successfully encoded
file. A runtime compatibility workaround also needs its own narrow provenance
and tests rather than silently becoming a fork of the provider.

Source S4: `NarrateAI/docs/OPENVOICE_AUDITION.md`, read in full, clean at
`7ca599dcd98e056d0f9077d8cedb781793ff79cc`, SHA-256
`48db5bffbc7cc21348bb6f47415610aa0799b1b0244183e4cc182c58f3c8fbc2`.
Recorded experiment: 18 September 2026; central review: 28 September.
No audio generation, listening approval or new provider verification occurred here.

## Original source map and limits

All sources were clean tracked files at
`NarrateAI@7ca599dcd98e056d0f9077d8cedb781793ff79cc`.
This identifies documentation, not a currently deployed artifact.

| ID | Repository-relative source | Reviewed evidence |
| --- | --- | --- |
| S1 | `docs/APPROACH2_RELIABILITY.md` | Full dated trial report: failures, partial repair, reused assets and rollout limits |
| S2 | `docs/SOURCE_RIGHTS.md` | Full metadata/approval contract and offline verification limits |
| S3 | `docs/CLIP_QUALITY.md` | Publishing, generation/review and Measurement sections; not every later media-quality section |

Graph coverage recorded no issue for these paths; the cited text was read
directly. No provider uptime, unattended daily reliability, final-video quality,
rights clearance or revenue improvement is established by this review. The
source trial did not include a worker crash, deliberate outage or multi-day soak.
Raw drafts and detailed operation records stay in the application repository.
