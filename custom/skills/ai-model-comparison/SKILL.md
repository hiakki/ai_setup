---
name: ai-model-comparison
description: Compare AI models, agent products, checkpoints and quantized deployments using configuration-matched evidence. Use when researching model choices, building benchmark or hardware comparison tables, ranking agents, or auditing claims that one model or quantization is better than another.
---

# AI model comparison

Compare the product the user would actually run. A provider, model family,
checkpoint, quantized artifact, API endpoint and agent application are different
units of comparison. A shared name does not make their results interchangeable.

## Identify the candidate and the evaluated system

For each candidate, record what is known and explicitly mark missing fields:

- Provider, exact model/checkpoint revision, base/instruct/reasoning variant,
  hosted endpoint/version or artifact repository, filename and commit/hash.
- Weight quantization and precision (including mixed formats), KV-cache precision,
  runtime/backend version, hardware, offloading and concurrency.
- Context limit, input/output and reasoning budgets, reasoning effort, sampling,
  chat/tool template, agent/controller version, tools and permissions.
- Evaluator, benchmark/dataset version and split, task count, harness version,
  metric and aggregation, retries/timeouts, evaluation date and source URL.

Use current primary sources: evaluator run manifests/methodology for scores,
artifact publishers for files and licenses, runtime documentation for support.
A mutable model name is not a revision pin. A model card can repeat base-model
results without evaluating the downloadable quantization. Do not infer missing
configuration details from a repository name or leaderboard title.

## Match evidence before assigning scores

Classify each result as **measured here**, **externally reported for the matched
configuration**, **unmatched reference**, **estimate**, or **unknown**. Retain
whether an external result is independent or publisher-reported. An evaluator's
estimated score is not a completed measurement.

- Never transfer a base-model, hosted, BF16, FP8 or high-reasoning score to another
  artifact, quantization, runtime or budget without matched evidence. Do not invent
  a generic percentage loss for 4-bit quantization or assume the ranking survives.
- A same-hardware rerun is not required to quote an external quality result, but
  changes in numerics, templates, tools or budgets must be disclosed and cannot be
  presented as measured equivalence. Latency and memory require hardware context.
- A common 0–100 scale does not make different benchmarks or index versions
  comparable. Do not average unrelated metrics or call index points accuracy.
- Perplexity, model size, active parameters, download size and chat smoke tests
  cannot substitute for end-to-end agent task completion. Fitting in RAM does not
  establish runtime compatibility, usable speed or reliable tool use.

## Present a comparison that the evidence supports

1. Maintain one canonical selection table per candidate set. Keep score columns,
   exact download/configuration, resources and selection notes together. Assign
   **NR / unmeasured** to an unavailable exact-product result; NR is not zero.
   Useful unmatched results may appear in a distinct column explicitly named
   **model-reference score (not this download)**, with evaluated setting and
   evidence status in every cell. Do not assign them to the exact-product column.
2. Sort measured/reported scores descending only within a comparable metric,
   version and evaluation protocol. Keep estimates in a separate group. Keep
   unknowns unranked. If the user needs one consolidated table sorted by a shared
   reference score, permit descending reference-score navigation with estimates
   labelled in every cell. Name the sort column; do not call it an exact-product
   quality rank. Do not mix unrelated metrics into that ordering.
3. State the ordering, evidence status, source/date, ties and uncertainty beside
   the table. A footnote does not fix a misleading score cell or inherited ranking.
   A small score gap alone does not establish a reliable winner.
4. Keep quality, speed, cost, memory and licensing separate unless a declared
   workload-specific utility function and supported inputs justify combining them.
   Separate measured resource use from planning estimates.
5. State whether a recommendation is based on measured workload quality or is
   merely a candidate to test for resource fit. When two exact products lack
   comparable results, say their relative quality is unknown.

## Make the comparison useful even when evidence is incomplete

An all-NR table is an evidence inventory, not a completed selection recommendation.
Do not stop there or make the user research every candidate themselves.

- Search for actual quantized-variant evaluations before declaring a gap. Check
  evaluator run details, artifact revisions and replacement history; distinguish
  quality tests from throughput tests and token-distribution similarity metrics.
- Preserve useful published measurements with their evaluated configuration and
  limitations. Missing CPU timing or a different test machine alone does not erase
  a quality result. Do not require identical hardware merely to discuss evidence.
- Give a small, ordered shortlist, a default starting choice, alternatives for
  quality/latency/memory priorities, and the evidence and uncertainty behind each.
  Label this as recommendation or trial order, not a measured quality ranking.
  Qualify confidence separately for quality, fit and speed.
- Where task-specific quantization scores exist, show them together under their
   actual metric and name differences from the proposed files. Use a separate
   score column in the canonical table; sort by one explicitly selected metric.
  Do not turn a writing score into a coding score or rename a generic Q4 result
  as a specific provider's UD-Q4 result. Do not invent numeric suitability ratings
  just to populate a table.
- Give a concrete shared workload rubric and decision rule for unresolved choices.
  Explain what to try first and what result would justify switching. Keep proposed
  scoring criteria distinct from scores already obtained.

## Resolve gaps with a fair workload evaluation

Propose the same representative tasks, verified acceptance criteria, inputs,
controller/tools, permissions and declared resource budgets for each candidate.
Record model-specific supported templates/settings rather than silently making
one candidate run incorrectly. Distinguish fixed-budget deployment comparisons
from maximum-capability comparisons; disclose unavoidable differences.

Measure verified task completion, tool-call validity, retries/failures, median/p95
latency, peak RAM/VRAM and cost per successful task. Preserve run manifests and raw
results; repeat enough trials to report variability. Label a custom workload score
as such, not as a reproduced public index. Do not launch expensive downloads or
paid evaluations beyond the user's authorized scope merely to fill a score cell.

Before delivery, check every scored row against its actual evaluated identity,
validate sorting within each evidence group, and remove conclusions that rely on
an unmatched configuration. Correct the table itself when an error is found.

## Required comparison review

When delegation is available and allowed, use an independent reviewer for a
substantial comparison or a repeated correction. Give the reviewer the user's
constraints, canonical table, metric definitions and evidence limitations while
continuing independent work. Do not claim review when it did not run.

Before finishing, verify: the requested table itself has score columns; every
candidate appears once in that selection table; ordering matches its declared
score; source, setting, estimate and artifact distinctions remain visible; and
the reader can choose without joining duplicate score, hardware and shortlist
tables. Fix the canonical table instead of adding another competing table.
