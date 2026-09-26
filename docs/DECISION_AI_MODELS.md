# Decision AI model selection

**Ranked comparison · CPU/GPU sizing · Pricing**

Research snapshot: **25 September 2026** · Audience: engineering and infrastructure teams

> **Recommendation:** evaluate **AutoJev-27B** first when GPU capacity is available. For a **32 GB CPU-only VM**, compare **Decider-4B BF16**, **SemIf-4B Q4**, and **Laya** on the same business tasks. Keep **Jev** as the hosted quality and cost reference.

This report covers **18 scored configurations and 14 additional variants**. Scores come from a shared published benchmark; resource allocations are planning estimates unless explicitly marked as publisher measurements. **No inference, latency, or memory tests were run for this report.**

**Contents:** [Rankings](#1-ranked-comparison) · [Trading score](#trading-score-scope-and-method) · [32 GB CPU options](#2-what-fits-on-a-32-gb-cpu-only-vm) · [4 GB options](#3-what-happened-to-the-4-gb-options) · [Additional GPU variants](#4-additional-gpu-variants) · [Pricing](#5-pricing-and-licensing) · [Selection plan](#6-how-to-choose-for-our-workload) · [Evidence](#appendix-evidence-and-sources)

## 1. Ranked comparison

### Read the score correctly

**Score /100** is the published **Decision Index 0.2** quality score, sorted highest to lowest. It combines 40 benchmarks across five equally weighted capability areas. **51.67 does not mean 51.67% accuracy.** Cost, throughput, and resource efficiency are assessed separately because no controlled measurements support combining them into one overall score.

Ranks apply to this report's selected configurations, not every model available online. Differences of 0.25 points or less are near-ties under the source methodology. Results belong to the named configuration; a larger, newer, or differently quantized variant does not inherit its score. [Methodology][index-method] · [Published results][index-data]

**Trading proxy /100*** = financial-news sentiment macro-F1 × 100 on the Decision Index's FinEntity task. This is a measured input-analysis capability, **not a validated score for buy/sell decisions, market prediction, or profitability**. See [scope and method](#trading-score-scope-and-method). The table remains sorted by general Decision Index score.

### Quality and deployment resources

**Host** = vCPU / total system RAM. **GPU memory** is additional to host RAM. All allocations below are **estimates**, except GPU figures marked **†**, which publishers report for their tested setup. A demonstrated configuration is not necessarily a minimum.

| Rank | Model / evaluated configuration | Score /100 | Trading proxy /100* | Host: vCPU / RAM | GPU memory or CPU path |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | [Jev 1.13][jev] | **51.67** | 86.98 | API client only | Provider-managed |
| 2 | [AutoJev-27B][autojev] | **50.94** | 92.90 | 8–16 / 128 GB | 80 GB |
| 3 | [Rune v1 · JD-Q6_K][rune-v1] | **47.23** | 85.00 | 8–16 / 64 GB | 96 GB†; minimum unknown |
| 4 | [Decider chat · Qwen3.6-27B][decider] | **46.08** | 81.83 | 8–16 / 128 GB | 80 GB, BF16 |
| 5 | [JEVfire · Qwen3.8-27B FP8][jevfire] | **45.73** | 80.32 | 8–16 / 64 GB | 48 GB, compatible GPU |
| 6 | [Winnow-12B · Q8][winnow12] | **45.05** | 91.74 | 8–16 / 32 GB | 16 GB† |
| 7 | [JoshuaSP Open Jev · DiffusionGemma][joshua] | **44.16** | 89.04 | 8–16 / 128 GB | H100 80 GB† |
| 8 | [Decider-35B-A3B · NVFP4][decider35q] | **43.50** | 85.24 | 8–16 / 64 GB | 32 GB, compatible Blackwell |
| 9 | [Decision Lux-9B][lux] | **38.98** | 81.81 | 8–16 / 32–64 GB | 24–32 GB, AMD gfx942 |
| 10 | [Xor · 35B-A3B][xor] | **38.77** | 88.74 | 8–16 / 128 GB | 2 × 96 GB†; minimum unknown |
| 11 | [Decider-4B · evaluated release][decider4] | **36.58** | 86.04 | 8 / 16–24 GB | CPU; optional 16 GB GPU |
| 12 | [Winnow-E4B · Q8][winnowe4] | **35.98** | 88.53 | 8 / 32 GB | 8.56 GiB peak†; plan 10 GB+ |
| 13 | [Kev-9B][kev9] | **35.41** | 88.38 | 8 / 32–64 GB | 24 GB |
| 14 | [Kev-4B][kev4] | **31.31** | 81.79 | 4–8 / 32 GB | 16 GB |
| 15 | [Decider-2B · FP8 HTTP][decider2] | **26.11** | 76.12 | 4–8 / 16 GB | 8 GB, FP8-compatible GPU |
| 16 | [SemIf · published 4B-Base entry][semif] | **25.70** | 65.96 | 4–8 / 32 GB | 12–16 GB BF16 planning case* |
| 17 | [Kev-0.8B][kev08] | **13.26** | 70.12 | 4 / 8–16 GB | 4 GB |
| 18 | [Laya · English checkpoint][laya] | **5.51** | 60.98 | 2–4 / 4–8 GB | CPU; optional 4 GB GPU |

These estimates assume **one loaded model, short text inputs, low concurrency, and runtime/OS headroom**. CPU allocations are starting points, not measured throughput requirements. Use each checkpoint's supported context limit; longer contexts and concurrent requests can require much more memory.

**Details that affect selection:**

- **AutoJev leads the open entries in this snapshot.** Its approximately 49 GiB of BF16 weights rule out a 32 GB CPU deployment of the released configuration.
- **Rune's 47.23 is v1.** The newer v3 BF16 release is listed separately below. The ranking links to the archived v1 revision.
- **Lux has a hardware restriction.** Its qualified runtime targets AMD gfx942; CPU/MPS are unsupported. Do not budget an arbitrary NVIDIA GPU solely from the memory figure. Lux and Xor are a near-tie.
- **Winnow's supported platforms use NVIDIA GPUs or Apple Silicon.** Its files may fit CPU RAM, but its CPU-only service has not been qualified here. E4B's published peak is for an 8K text test.
- **Kev's 32 GB Mac support uses an integrated GPU.** It does not establish support for a Linux CPU-only VM.
- **SemIf's scored identity differs from the recommended CPU setup.** The index names Qwen3.5-4B-Base; the project documents Qwen3.5-4B for Q4 CPU use. *The BF16 resource estimate above is a planning case, because the summary does not establish the benchmark precision.*
- **Decider chat is an engine configuration using Qwen3.6-27B**, distinct from the trained Decider checkpoints. The 2B score is specifically FP8; its BF16 CPU variant is unranked.

### Trading score: scope and method

The new column uses **FinEntity**, which tests whether a financial-news snippet is positive, negative, or neutral toward a named company. This is relevant when a trading workflow consumes news. It does not test trade direction, entry/exit timing, position sizing, chart interpretation, execution, or risk-adjusted returns. [FinEntity paper][finentity] · [Benchmark results][index-data]

**Calculation:** `Trading proxy = 100 × results["39"].score`, rounded to two decimals. The metric is raw macro-F1: an equal-weight average of the positive, negative, and neutral class F1 scores. It is not percentage accuracy and is not chance-corrected like the general index.

All 18 ranked configurations have results for the suite's **979 cases**. The 17 open entries report 979 answered with no unsupported cases or errors; Jev's reference lists 979 cases. The new values use the same dated snapshot and exact engine identities as the existing comparison. **NR** means no matched FinEntity result for that variant; another precision or checkpoint cannot supply it.

**How to use the column:** AutoJev-27B scores **92.90**, Winnow-12B Q8 **91.74**, and the evaluated Decider-4B **86.04**. These are candidates for financial-news interpretation. The Decider-4B recommendation for a 32 GB VM remains an evaluation starting point; **neither this score nor its general score validates the proposed BF16 CPU deployment for trading**. Small differences are not evidence of a statistically reliable lead; this snapshot provides no confidence intervals for the comparison. [Published results][index-data]

**Actual trading-decision score: not established for any configuration by the evidence used here.** To obtain one, fix the asset universe, decision horizon, inputs, strategy, and objective first. Then compare every candidate against the same baseline using time-ordered, point-in-time data and out-of-sample walk-forward tests. Check model/data cutoff dates for contamination and use forward paper trading when historical isolation cannot be established. Include fees, spread, slippage, latency, liquidity, market impact, and delisted assets where applicable; report net return, drawdown, turnover, and uncertainty. Execution assumptions materially affect simulated results. [Execution and cost modeling][trading-costs]

## 2. What fits on a 32 GB CPU-only VM?

**Several options fit on paper.** The assumption is a Linux VM with **32 GB total RAM, no GPU, one model loaded**, and short requests. “CPU documented” means the publisher supports a CPU path; it does not mean we measured the proposed allocation.

For the first comparison, use **Decider-4B BF16** as the trained decision baseline, **SemIf-4B Q4** as the lower-memory alternative, and **Laya** for narrower classification tasks.

### CPU paths and estimated allocations

The two configurations with a published reference score appear first, in descending score order. **NR = not ranked:** no directly comparable score for that exact configuration. NR is not zero.

| Configuration | Reference score | Trading proxy /100* | vCPU | Total RAM | CPU status |
| --- | ---: | ---: | ---: | --- | --- |
| [Decider-4B · BF16 candidate][decider4] | **36.58*** | 86.04† | 8 | 16–24 GB | CPU eager documented |
| [Laya English][laya] | **5.51** | 60.98 | 2–4 | 4–8 GB | CPU documented |
| [SemIf + Qwen3.5-4B · Q4_K_M][semif] | NR | NR | 4–8 | 6–8 GB | llama.cpp CPU documented |
| [Decider-2B · BF16][decider2] | NR | NR | 4–8 | 8–12 GB | CPU eager documented |
| [Decider-0.8B · BF16][decider08] | NR | NR | 4 | 4–8 GB | CPU eager documented |
| [OpenJev (lookski) + Qwen3-4B-Instruct-2507 · FP32][lookski] | NR | NR | 8 | 24–28 GB | CPU documented; less headroom |
| [Laya multilingual][laya-multi] | NR | NR | 2–4 | 4–8 GB | CPU documented |
| [Laya typed-decisions][laya-typed] | NR | NR | 2–4 | 4–8 GB | CPU documented |
| [SemIf + Qwen3-0.6B · Q8][semif] | NR | NR | 2 | 2–3 GB | Exact CPU configuration needs testing |
| [SemIf + MiniCPM5-2B · Q4][semif] | NR | NR | 2–4 | 3–4 GB | Exact CPU configuration needs testing |

No reference score above was measured on this proposed VM. **\*Decider-4B's 36.58 is a model reference:** the index summary does not identify its evaluated precision or exact weight revision, so the proposed BF16 CPU configuration does not have a confirmed score. **†The same restriction applies to its 86.04 trading proxy.** Decider-2B BF16 cannot inherit the FP8 score of 26.11, and SemIf Q4 cannot inherit 25.70 from the published 4B-Base entry.

### Potential fits requiring runtime qualification

| Configuration | Estimated CPU allocation | Remaining question |
| --- | --- | --- |
| [Winnow-12B Q8][winnow-runtime] | 8–16 vCPU / 20–28 GB RAM | Does its custom decision-serving path work correctly on Linux CPU? |
| [Winnow-E4B Q8][winnow-runtime] | 8 vCPU / 12–20 GB RAM | Same qualification needed; smaller memory footprint |

A GGUF file fitting in RAM does not establish a working endpoint or acceptable latency. Kev's Apple Silicon results, Decider's NVFP4 GPU kernels, and SemIf's CUDA EXL3 bridge also cannot establish a CPU-only fit.

Keep the allocations **per alternative**, not additive models to run together. CPU memory bandwidth and instruction support can dominate latency; adding vCPU alone does not guarantee a faster service.

## 3. What happened to the 4 GB options?

**SemIf still belongs in the comparison.** The earlier question prioritized fitting a small machine; the unrestricted ranking prioritizes broad decision quality. Those produce different recommendations.

SemIf is an inference engine whose quality and memory use depend on the selected model. Its **3.01 GB Qwen3.5-4B Q4 file** needs additional runtime memory, so **6–8 GB total RAM** is the planning range. A **4B-parameter model**, a **4 GB download**, and a **4 GB VM** are different quantities.

For a strict **4 GB CPU VM**:

| Candidate | Assessment |
| --- | --- |
| SemIf + Qwen3-0.6B Q8 | Most comfortable estimated footprint here: 2–3 GB. Test the exact runtime and task quality. |
| SemIf + MiniCPM5-2B Q4 | Borderline at 3–4 GB; little headroom. |
| Laya or Decider-0.8B | Estimates start at 4 GB; profile before treating them as fits. |
| SemIf + Qwen3.5-4B Q4 | Allocate 6–8 GB instead. |
| Decider-2B BF16 | Allocate 8–12 GB instead. |

**Why SemIf's reported scores differ:** its author reports 81.3% balanced accuracy for native 4B BF16 on 144 authored decisions, and 95.8% for a 27B EXL3 setup on that fixture. Neither is a Q4 CPU score or the same metric as the broader Decision Index. The smaller public-subset comparison reports 84.5% agreement against a published Jev reference of 88.3%. These are useful evaluation leads, not interchangeable rankings. [SemIf evaluation][semif] · [27B bridge][semif27]

Laya also has separate checkpoints: English, multilingual, and typed-decisions. The publisher reports 76.6% for typed-decisions versus 36.2% for the base English model on its 2,000-decision suite. This supports task specialization; it does not replace the English checkpoint's broader index result. English defaults to 512 tokens; multilingual defaults to 1,024. Loading multiple checkpoints increases RAM. [Laya model cards][laya]

## 4. Additional GPU variants

These six variants complete the **14 unranked configurations** alongside the eight NR CPU variants above. They are retained because they may be useful, but cannot be inserted into the common ranking without matched evidence.

Host allocations are estimates. Published GPU configurations are marked **†**; other GPU allocations are estimates.

| Configuration | Trading proxy /100* | Host: vCPU / RAM | GPU memory | Quality evidence |
| --- | ---: | --- | --- | --- |
| [Rune v3 · BF16][rune] | NR | 8–16 / 128 GB | 96 GB† | Author reports index 53.39 |
| [Kev-27B][kev27] | NR | 8–16 / 128 GB | 80 GB† | No matched index entry |
| [SemIf + Qwen3.8-27B · EXL3][semif27] | NR | 8–16 / 64 GB | 24–32 GB CUDA | 95.8% on author's 144 decisions |
| [Decider-35B-A3B · BF16][decider35] | NR | 8–16 / 128 GB | 80 GB† | Ranked result uses NVFP4 |
| [Winnow-12B · F16][winnow12] | NR | 8–16 / 64 GB | 32 GB | Ranked result uses Q8 |
| [Winnow-E4B · F16][winnowe4] | NR | 8 / 32–64 GB | 24 GB | Ranked result uses Q8 |

Rune v3's author-run score does not establish a lead over the independently published Jev result. SemIf's 27B bridge is CUDA-based; its example allocates 22.5 GB to GPU use, which informs the 24–32 GB planning estimate.

Mixture-of-experts names such as “26B-A4B” describe total and active parameters. Fewer active parameters reduce compute; they do not mean only 4B parameters need weight storage. Host RAM and VRAM remain separate budgets.

## 5. Pricing and licensing

### Hosted Jev

**$0.042 per million input tokens; output tokens are free.** Shared state is processed once within a request. A request can contain multiple decisions, so requests and decisions are not interchangeable billing units. [Official pricing][jev]

| Example workload | Input tokens | API charge |
| --- | ---: | ---: |
| 1 million requests × 1,000 tokens | 1 billion | **$42** |
| 1 million requests × 5,000 tokens | 5 billion | **$210** |
| 1 million requests × 10,000 tokens | 10 billion | **$420** |

These are arithmetic examples, excluding taxes, custom agreements, and application costs.

### Self-hosted options

**All self-hosted candidates in the ranked and NR tables have no published per-token license fee under the cited terms.** Infrastructure and operations are additional; “$0 model fee” does not mean free hosting.

| Family / project | Published license | Model/software fee |
| --- | --- | --- |
| AutoJev; Winnow | Apache-2.0 weights; MIT serving code | $0 |
| Rune; Kev; Decider; Lux; Xor; Laya | Apache-2.0 model releases | $0 |
| SemIf; JEVfire; JoshuaSP Open Jev; lookski OpenJev | MIT engines; selected base-model terms apply | $0 engine fee |

License sources are the model cards and repositories linked in each model row. Open weights do not imply that the complete training process is reproducible: AutoJev and Winnow do not release their exact curated training corpora.

**Naming exception:** [openjev/openjev][openjev-nc] is a different trained model with **CC BY-NC 4.0 weights**. It is excluded from the commercial shortlist unless separate permission is obtained. Do not infer its license from an unrelated MIT repository with a similar name.

### Compare actual serving cost

A portable cost-per-request figure needs measured throughput and a chosen provider. This report does not invent either.

```text
Cost per 1,000 completed decisions
  = total serving cost during the period
    ÷ completed decisions during the same period
    × 1,000
```

Include compute, idle replicas, storage, networking, retries, and operations consistently. Compare at the same acceptable error rate; an inexpensive incorrect decision can create more business cost than it saves.

## 6. How to choose for our workload

The first evaluation should answer a business question, not reproduce a leaderboard for its own sake.

| Priority | Compare first | Decision to make |
| --- | --- | --- |
| Broad quality, GPU available | AutoJev-27B against Jev | Does local quality justify operating the service? |
| 32 GB Linux CPU VM | Decider-4B BF16, SemIf-4B Q4, Laya English | Which meets our accuracy and latency targets? |
| Strict 4 GB CPU VM | SemIf Qwen3-0.6B Q8; smaller candidates above | Can the exact runtime and task quality meet requirements? |
| Explore newer GPU alternatives | Rune v3, Kev-27B, Decider-35B, SemIf-27B | Do author-reported gains hold on our cases? |

Use held-out examples of the actual decisions: routing, escalation, policy judgments, and scoring. Include missing evidence, ambiguous cases, long inputs, and relevant languages.

For each candidate, record:

1. **Exact configuration:** weight revision, engine, precision, prompt, context cap, and calibration.
2. **Business quality:** incorrect automatic actions, missed escalations, abstention rate, and per-task accuracy.
3. **Service performance:** end-to-end p50/p95/p99, sustained throughput, error rate, cold starts, peak RAM, and peak VRAM.
4. **Operating cost:** cost per completed decision and per correctly automated outcome.

Keep calibration data separate from the final test set. Exercise the same authenticated gateway and concurrency that callers will use. A valid typed response can still be wrong; model confidence needs validation before it controls consequential actions.

**Selection rule:** choose the candidate that meets the agreed quality and latency targets at the lowest measured operating cost. The estimates here support choosing experiments; they are not final Kubernetes requests or limits.

## Appendix: evidence and sources

### Benchmark provenance

- **Dataset:** Decision Index 0.2; this snapshot contains 51 open entries plus Jev.
- **Score field:** `scores.balanced_skill`, out of 100.
- **Snapshot timestamp:** `2026-09-25T10:35:07+00:00`.
- **JSON SHA-256:** `7a1feffba0016e70773d950ff34d8904d8af6e02ddcdfc1f7445faee650a42e1`.
- **Sources:** [methodology][index-method], [leaderboard][index-ui], [machine-readable results][index-data].

The method adjusts for chance and unanswered/unsupported cases, then averages within five equally weighted areas: knowledge/reasoning, language, retrieval/classification, tools/automation, and arts/human taste. An index score is neither raw accuracy nor accuracy only on answered questions.

The live source is mutable; the hash identifies the researched snapshot. Some entries lack complete weight-revision pins in the summary. Obtain the original run manifests for exact reproduction. Different GPU/CPU backends and precisions can change outputs, and local GPU latency cannot be directly ranked against remote HTTP latency.

### Resource evidence

Publisher measurements, artifact sizes, and supported backends informed the estimates. Key references:

| Evidence | Source |
| --- | --- |
| CPU support and small-model sizes | [Decider runtime][decider], [4B][decider4], [2B][decider2], [0.8B][decider08] |
| CPU GGUF path; 3.01 GB 4B Q4 file | [SemIf][semif] |
| Small files: 639 MB Qwen3-0.6B; 1.56 GB MiniCPM5-2B | [SemIf configurations][semif] |
| CPU FP32 path; approximately 16 GB weights | [lookski OpenJev][lookski] |
| GPU/Mac platform support | [Kev][kev], [Winnow serving runtime][winnow-runtime] |
| 12.67 GB Q8 / 23.83 GB F16 files | [Winnow-12B][winnow12] |
| 8.01 GB Q8 / 15.05 GB F16 files | [Winnow-E4B][winnowe4] |
| AMD runtime restriction | [Lux runtime][lux-runtime] |
| Xor validation and 120 GB disk requirement | [Xor model card][xor] |
| Large model weight and runtime requirements | [AutoJev][autojev], [Rune][rune], [Kev-27B][kev27], [Decider-35B][decider35] |

**Evidence limit:** this is a source-based selection report. It contains no locally measured quality, latency, throughput, or serving-memory results. Recheck mutable prices, licenses, weight revisions, and runtime support before procurement or deployment.

[finentity]: https://aclanthology.org/2023.emnlp-main.956/
[trading-costs]: https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/key-concepts
[index-method]: https://github.com/apolinario/decision-index
[index-data]: https://multimodalart-jev-decision-index.static.hf.space/data/index.json
[index-ui]: https://huggingface.co/spaces/multimodalart/jev-decision-index
[jev]: https://docs.typesafe.ai/models
[autojev]: https://huggingface.co/denis-pplx/autojev-27b
[rune-v1]: https://huggingface.co/surogate/rune-26b-a4b-GGUF/tree/2a155046d99949c8d8b413e213a78b4dc724dcb6
[rune]: https://huggingface.co/surogate/rune-26b-a4b-GGUF
[decider]: https://github.com/Mapika/decider
[decider35q]: https://huggingface.co/Mapika/decider-35b-a3b-nvfp4
[decider35]: https://huggingface.co/Mapika/decider-35b-a3b
[decider4]: https://huggingface.co/Mapika/decider-4b
[decider2]: https://huggingface.co/Mapika/decider-2b
[decider08]: https://huggingface.co/Mapika/decider-0.8b
[jevfire]: https://github.com/kikoncuo/jevfire
[winnow12]: https://huggingface.co/EldanRing/Winnow-12B
[winnowe4]: https://huggingface.co/EldanRing/Winnow-E4B
[winnow-runtime]: https://github.com/EldanRing/winnow-inference
[joshua]: https://github.com/JoshuaSP/open-jev
[lux]: https://huggingface.co/llm-semantic-router/Decision-1.0-Lux-9B
[lux-runtime]: https://huggingface.co/llm-semantic-router/Decision-1.0-Lux-9B/blob/main/RUNTIME.md
[xor]: https://huggingface.co/juspay/xor
[kev]: https://github.com/jaredpalmer/kev
[kev27]: https://huggingface.co/jaredpalmer/kev-27b
[kev9]: https://huggingface.co/jaredpalmer/kev-9b
[kev4]: https://huggingface.co/jaredpalmer/kev-4b
[kev08]: https://huggingface.co/jaredpalmer/kev-0.8b
[semif]: https://github.com/TheoLeeCJ/SemIf-OpenJev
[semif27]: https://github.com/TheoLeeCJ/SemIf-OpenJev/blob/master/exl3-bridge/README.md
[lookski]: https://github.com/lookski/openjev
[laya]: https://huggingface.co/convaiinnovations/laya
[laya-multi]: https://huggingface.co/convaiinnovations/laya-multilingual
[laya-typed]: https://huggingface.co/convaiinnovations/laya-typed-decisions
[openjev-nc]: https://huggingface.co/openjev/openjev
