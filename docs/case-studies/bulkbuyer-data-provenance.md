# bulkBuyer: data freshness, scoring and reproducible observations

Reviewed: 28 September 2026. Search terms: bulkBuyer, data pipeline, provenance,
freshness, scoring, eligibility, historical reconstruction, cache, backfill,
scheduler, reporting, point-in-time data.

This case preserves data-engineering lessons from a research application's
reliability record. It does not reproduce investment rules, current market
schedules, portfolio allocations or financial recommendations. No external
archive, report export or application job was run for this review.

## Concrete failures and decisions

| Source observation or contract | Transferable action | Evidence boundary |
| --- | --- | --- |
| An official archive downloaded from a workstation but returned access errors from the deployment network. Saved reports consequently lacked verified closes. | Test provider access from the actual execution host. A workstation probe and application health response do not verify a scheduled production data path. | The document records the dated access failure. A one-time authorized transfer did not establish automatic delivery. |
| A plausible quote could exist while final daily evidence was missing. | Separate provisional observations from finalized source facts. Validate session/date, schema, units, identities, row coverage and conflicting records before use. | The source reports cross-archive field comparisons for selected dates, not provider-wide accuracy or a publication SLA. |
| Old data could remain usable-looking after a failed refresh. | Reuse only explicitly identified, integrity-checked cache data; retain its date. Missing new data stays missing, with eligibility withheld where required. | Do not relabel yesterday's file or silently substitute a different field such as last trade for final close. These are recorded safeguards, not newly tested behavior. |
| Historical repairs could introduce facts learned after the requested cutoff. | Retain observation cutoff, publication evidence and actual collection time separately. Label reconstructed rows; do not insert them as prospective observations. | Timestamp checks prevent known leakage; they do not manufacture missing point-in-time provider evidence. |
| A heuristic score looked more authoritative than its validation justified. | Keep rank, eligibility, allocation decisions and predictive calibration separate. Preserve a usable score's definition without converting it to a probability or return forecast. | The source explicitly labels predictive performance unvalidated, even after collecting outcomes. Software checks do not establish predictive accuracy. |
| Refreshes and model changes could rewrite the comparison baseline. | Retain the first prospective observation and version/configuration identity; keep reconstructed, overlapping and current-model samples distinguishable. | Descriptive observed changes are not executions or independent validation samples. Missing coverage must remain visible. |
| A later daily publication retry could leave the weekly aggregate stale. | After a successful retry, refresh dependent outputs deliberately and verify the exported result. | A deployment does not rewrite previously generated reports. Regenerate an explicitly chosen artifact and inspect it. |

For another scoring or reporting system, first define what a number means, which
evidence makes it eligible, and which timestamps govern its use. An honest
unavailable result is preferable to a fabricated current value; that does not
justify removing useful, clearly labelled heuristic scores.

## Reuse and verification

Search `ai-setup search "bulkbuyer provenance"`. Use
[auditable calculations](../../custom/skills/auditable-business-workflows/references/source-of-truth-and-calculations.md)
and [reliable operations](../../custom/skills/reliable-web-app-operations/SKILL.md).
Adopt, adapt or reject the data controls for the target's sources and freshness
contract. Test wrong-date successful responses, changed bytes, missing fields,
cutoff violations, retries and the final downstream report.

## Source and limits

Source: `bulkBuyer/docs/RESEARCH_RELIABILITY.md`, read in full as a clean tracked
file at `bulkBuyer@1e41dd7aa47d0d174fd5d8c1efda882e1333fb33`.
SHA-256: `308e7e603d58b276e2093559b0fdd221c080ec1b965b1d296af6519be2c15478`.
The record includes an access incident dated 19 September 2026 and describes
implemented safeguards, operator checks and fixture/mocked tests. Graph coverage
recorded no issue for this path; this review used the actual document text.

No fresh implementation audit, schedule execution, external Sheet write, email,
provider-accuracy check or investment-performance validation was performed.
Private endpoints, report identifiers and source datasets remain with the owner.
