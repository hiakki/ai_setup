# Agentic AI models: CPU-only choices, benchmark scores and cost

**Updated 26 September 2026.** The [common score tables](#common-score-for-comparing-models) below describe the evaluator's model/settings, not the exact deployment products in section 1. For a **32 GB RAM machine with no GPU**, **Qwen3.5-9B Q4_K_M** remains a starting point with useful memory headroom: approximately **5.68 GB of weights, 12–18 GB total RAM, 8 vCPU, 0 GB VRAM**. This is a resource-fit candidate to test, not a demonstrated quality winner. No CPU deployment in this report was benchmarked locally.

An agent needs both a model and software that executes its tools. The tables compare models; LiteLLM can provide the gateway, while an agent controller manages tool execution and state. The separate [decision-model comparison](DECISION_AI_MODELS.md) covers specialist decision engines.

## Common score for comparing models

**Common score = Artificial Analysis Intelligence Index v4.3.2, on its published 0–100 scale; higher is better.** Values below are the evaluator's displayed, rounded index points, checked on **26 September 2026**. They are not percentages of tasks completed. We do not rescale the best model to 100 or calculate a new average from unrelated benchmarks.

The index uses ten evaluations, weighted across **Agents 30%, Coding 20%, Scientific Reasoning 20%, General 30%**. Agent evaluations are AA-Briefcase v1.1, GDPval-AA v2.1 and AutomationBench-AA; coding includes Terminal-Bench 4.0 and SciCode. This gives a broad common reference, not a dedicated video-editing or coding-agent success rate. [Evaluator methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)

**Reported** means the model page publishes the score without identifying it as estimated in its model-specific FAQ. **Estimated** means that FAQ explicitly labels it estimated: independent evaluation is pending, so treat its placement as provisional. **NR** means a matching score was not established in this review, not zero. Reference tables are sorted by descending AA value, with reported/estimated status visible. This is reference-score navigation, not a measured ranking of proposed downloads. Ties have no preferred order; small differences do not establish a reliable winner. Exact artifact revisions and runtime equivalence to our proposed deployments have not been established.

### Hosted and larger-model AA references

CPU candidates and their AA references appear **once**, in the [consolidated CPU comparison](#1-models-for-32-gb-ram--no-gpu-required).

| Model / AA evaluation setting | AA reference score /100 | Evidence |
|---|---:|---|
| [GPT-6 Astra · max](https://artificialanalysis.ai/models/gpt-6-astra) | **53** | Reported |
| [GPT-5.6 Sol · max](https://artificialanalysis.ai/models/gpt-5-6-sol) | **47** | Reported |
| [GLM-5.3 · max](https://artificialanalysis.ai/models/glm-5-3) | **45** | Reported |
| [Kimi K3 · max](https://artificialanalysis.ai/models/kimi-k3) | **44** | Reported |
| [Claude Opus 4.8 · adaptive/max](https://artificialanalysis.ai/models/claude-opus-4-8) | **42** | Reported |
| [GLM-5.3-Flash](https://artificialanalysis.ai/models/glm-5-3-flash) | **42** | Reported |
| [Qwen3.8-Flash-Next](https://artificialanalysis.ai/models/qwen3-8-flash-next) | **40** | Reported |
| [Qwen3.8-2.4T-A95B](https://artificialanalysis.ai/models/qwen3-8-2-4t-a95b) | **40** | Reported |
| [DeepSeek-V4.1-Flash · max](https://artificialanalysis.ai/models/deepseek-v4-1-flash) | **39** | Reported |
| [DeepSeek-V4-Pro-0813 · max](https://artificialanalysis.ai/models/deepseek-v4-pro) | **36** | Reported |
| [GPT-5.3-Codex · xhigh](https://artificialanalysis.ai/models/gpt-5-3-codex) | **33** | Estimated |
| [MiniMax M3](https://artificialanalysis.ai/models/minimax-m3) | **29** | Reported |

**Unranked:** Tencent Hy4-preview — **NR**, no matched AA result established.

**Coverage across this table and the CPU comparison: 24 model identities; 23 AA reference scores, of which eight are estimated.** Row links identify the evaluator's model pages, not the model publisher's headline claims. Preserve the index version, reasoning setting, date and estimate status together when updating. Older AA index versions are not interchangeable with v4.3.2.

**How to use this comparison:** use these results to identify models worth investigating, then seek evidence for the exact products and workload you would run. The CPU table uses the same reference-score order for lookup; that order does not establish relative quality of its quantised downloads. A value of 34 versus 42 does not mean “81% of Claude's quality.” A reported AA score does not establish a score for our proposed GGUF precision, CPU backend, 4K context and agent setup.

**Across the two documents:** this report uses **AA Intelligence Index v4.3.2**; `DECISION_AI_MODELS.md` uses **Decision Index 0.2**. Both provide a common score within their own candidate set. Their numbers cannot be ranked against one another, even though both use a 100-point scale. For a score shared across both families, they would need evaluation on the same tasks and scoring protocol; no such result is claimed here.

## 1. Models for 32 GB RAM — no GPU required

**These are CPU-only configurations; a GPU is not required.** Use a compatible [llama.cpp](https://github.com/ggml-org/llama.cpp) build and the linked quantisation, rather than the original BF16 weights. Model/runtime compatibility and peak RAM still need verification on your machine.

RAM figures are **planning estimates for the whole machine**, including weights, inference buffers/cache and 4–6 GB for a lean OS and controller. Assumptions: **text only, 4,096 total context tokens, one active request, no additional prompt-cache allocation**. Browsers, builds and other services need separate headroom. A 32 GB machine has approximately 29.8 GiB.

**Starting choice:** Qwen3.5-9B Q4_K_M for a shared development server; Qwen3.8-27B UD-Q4_K_M as the first coding trial on a dedicated inference machine when longer waits are acceptable. These are provisional resource/workload recommendations. Use the selection note in each row, not its position, to choose.

**One comparison table; sorted descending by AA model-reference score.** Every configuration below requires **no GPU (0 GB VRAM)**. The AA column names the evaluated model setting and evidence status; it is **not a score measured for the linked download**. The local-workflow score is unmeasured for all candidates. Related writing scores identify different evaluated variants and do not affect row ordering.

| Candidate / quantised download / weights | AA model-reference score /100 — **not this download** | Related-variant writing score — **not this download** | Local workflow /100 | Total RAM / vCPU estimates | Selection note |
|---|---|---|---|---|---|
| **Qwen3.8-27B** · [UD-Q4_K_M · 16.46 GB](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) | [**34**](https://artificialanalysis.ai/models/qwen3-8-27b) · **Reported** · xhigh | 59.4 · Q4_K_M, default xhigh; **UD file not matched** | Unmeasured | 24–30 GB / 12–16 vCPU | Dedicated-server coding trial; related older Q4 evidence below. |
| **Gemma 4 26B A4B IT** · [Q4_0 · 14.62 GB](https://huggingface.co/ggml-org/gemma-4-26B-A4B-it-GGUF) | [**17**](https://artificialanalysis.ai/models/gemma-4-26b-a4b) · **Estimated** · reasoning | 41.0 · **QAT-Q4_0**, reasoning on; different checkpoint | Unmeasured | 22–30 GB / 8–16 vCPU | Larger alternative to test for responsiveness; no measured CPU speed lead. |
| **GLM-4.7-Flash** · [Q4_K_M · 18.31 GB](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF) | [**15**](https://artificialanalysis.ai/models/glm-4-7-flash) · **Estimated** · reasoning | Not established | Unmeasured | 26–30 GB / 8–16 vCPU | Tightest RAM estimate; reserve inference capacity before testing. |
| **Gemma 4 12B IT** · [Q4_0 · 7.22 GB](https://huggingface.co/ggml-org/gemma-4-12B-it-GGUF) | [**14**](https://artificialanalysis.ai/models/gemma-4-12b) · **Estimated** · reasoning | 45.1 · **QAT-Q4_0**, reasoning on; different checkpoint | Unmeasured | 14–20 GB / 8–12 vCPU | Mid-size alternative; writing reference needs the named QAT variant. |
| **Qwen3.5-9B** · [Q4_K_M · 5.68 GB](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) | [**14**](https://artificialanalysis.ai/models/qwen3-5-9b) · **Estimated** · reasoning | Not established | Unmeasured | 12–18 GB / 8 vCPU | **First trial on a shared development server**; leaves room for builds/apps. |
| **Qwen3.5-4B** · [Q4_K_M · 2.74 GB](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) | [**13**](https://artificialanalysis.ai/models/qwen3-5-4b) · **Estimated** · reasoning | Not established | Unmeasured | 8–12 GB / 4–8 vCPU | Lower-memory fallback if the 9B baseline competes with the app. |
| **gpt-oss-20b** · [MXFP4 · 12.11 GB](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF) | [**9**](https://artificialanalysis.ai/models/gpt-oss-20b) · **Reported** · high | Not established | Unmeasured | 18–26 GB / 8–16 vCPU | Alternative requiring correct Harmony/template handling. |
| **Gemma 4 E4B IT** · [Q4_0 · 4.59 GB](https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF) | [**9**](https://artificialanalysis.ai/models/gemma-4-e4b) · **Estimated** · reasoning | Not established | Unmeasured | 10–16 GB / 4–8 vCPU | Smaller-memory alternative; check task quality before adopting. |
| **Devstral Small 2 24B Instruct 2512** · [Q4_K_M · 14.33 GB](https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF) | [**8**](https://artificialanalysis.ai/models/devstral-small-2) · **Reported** · setting not specified | Not established | Unmeasured | 22–30 GB / 8–16 vCPU | Coding alternative with limited RAM headroom. |
| **LFM2.5-8B-A1B** · [Q4_K_M · 5.16 GB](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-GGUF) | [**7**](https://artificialanalysis.ai/models/lfm2-5-8b-a1b) · **Estimated** · setting not specified | Not established | Unmeasured | 10–16 GB / 4–8 vCPU | Small-footprint alternative; check its commercial licence. |
| **Ministral 3 14B Instruct 2512** · [Q4_K_M · 8.24 GB](https://huggingface.co/unsloth/Ministral-3-14B-Instruct-2512-GGUF) | [**6**](https://artificialanalysis.ai/models/ministral-3-14b) · **Reported** · non-reasoning/Instruct | Not established | Unmeasured | 16–24 GB / 8–12 vCPU | Mid-size Instruct alternative; do not use Reasoning checkpoint scores. |

**Score scope:** AA values use v4.3.2, checked 26 September 2026. The related writing results use the English AI-judged leaderboard snapshot of 25 September: Q4_K_M with default xhigh for Qwen and QAT-Q4_0 with reasoning on for Gemma. They are relative preference scores, not success percentages. QAT-Q4_0 is a different checkpoint; generic Q4_K_M does not identify Unsloth UD-Q4_K_M. No exact-file match or CPU-speed result is claimed. [Writing evaluator and methodology](https://aiwritingbenchmark.com/local-ai/)

**Coding evidence:** Quesma's 26 August study reports its Unsloth Qwen3.8-27B Q4_K_M matching its BF16 result on Terminal-Bench 2.1. It used GPU inference, xhigh, 98K context, F16 KV cache and a three-hour timeout over 89 tasks. Its 4-bit files were **v2 files subsequently replaced**. That supports a coding trial, not AA 34 for today's UD-Q4_K_M or equivalence under our 4K CPU budget. [Original experiment](https://quesma.com/blog/qwen38-27b-quantizations-benchmarked/)

**Qwen UD-Q4_K_M versus Gemma Q4_0:** their exact-product quality ordering remains unestablished. The AA reference column is useful background, not evidence that Qwen's download scores 34 or beats Gemma's download. Gemma's [MoE architecture](https://huggingface.co/google/gemma-4-26B-A4B-it#mixture-of-experts-moe-model) motivates a responsiveness trial; CPU speed and workload quality must still be measured.

Reserve 30–50 GB SSD for a smaller candidate, or 50–80 GB for a larger one. Qwen3.8-27B, Gemma 4 26B A4B, GLM-4.7-Flash and Devstral Small 2 have little spare RAM; start at 4K context and measure peak usage. Do not count swapping as a successful fit. CPU memory bandwidth affects speed, and dense 24–27B models can be slow despite fitting. No CPU tokens/second or task latency was measured here.

### A common score for your actual projects

Use **Local workflow acceptance v1**, a proposed 20-task test for this web-development workload. Freeze the tasks, fixtures and pass criteria before running any model. This score is **not yet measured** and does not reproduce AA.

| Category | Tasks | Points | Representative checks |
|---|---:|---:|---|
| Web/business application changes | 10 | 50 | Bounded bug fixes and features; hidden tests verify validation, permissions, calculations and UI states. |
| Tool use and structured output | 5 | 25 | Correct tool arguments, API pagination, schema-valid data and a media-job command against safe fixtures. |
| Content and editing plans | 3 | 15 | Product copy, a short script and an edit plan meeting a fixed brief; review blind against a written checklist. |
| Recovery | 2 | 10 | Recover from a tool timeout and missing input without inventing a successful result. |

**Score = 5 × tasks passed, out of 100.** A pass requires every task-specific acceptance check within the same declared time/tool budget; a timeout or unresolved task scores zero. Run the same 20 tasks three times per candidate and report the mean and range, with median/p95 task time and peak RAM separately. Treat unsafe writes or failed permission boundaries as disqualifying regardless of aggregate score.

Suggested initial decision rule: keep the baseline if it achieves **at least 80/100**, has no disqualifying failures, fits without swapping, and meets your task deadline. These are proposed acceptance thresholds, not published model capabilities. Switch only when a challenger improves the tasks that matter within the same limits; if quality is tied, prefer lower latency and memory. The actual CPU model, memory bandwidth and competing services must be recorded before making speed predictions.

## 2. Scores, including Codex and Claude references

**Task-specific scores below are published percentages; higher is better.** They describe the evaluated model and agent setup, **not a measured score for the CPU quantisations above**. Use the [common AA index](#common-score-for-comparing-models) for the broad comparison; these separate diagnostics explain where performance differs. Averaging these heterogeneous columns ourselves would not reproduce that index.

- **BFCL v4:** function/tool calling.
- **τ²-bench:** multi-turn support workflows; aggregate and individual-domain scores are distinct.
- **SWE-bench Verified:** fixing real repository issues.
- **Terminal-Bench:** terminal tasks; **2.0 and 2.1 are different benchmarks**.
- **DeepSWE v1.1:** repository-level engineering tasks.

**NR** means no matching result was established in the cited sources, not zero. “Codex” names a product: reference rows therefore specify its underlying model.

### Small-model results and larger-model anchors

Rows are alphabetical. Evaluators, settings and task coverage differ, so these diagnostics do not establish a controlled overall ranking.

| Model / evaluation setting | BFCL v4 | τ²-bench aggregate | SWE-bench Verified | Terminal-Bench |
|---|---:|---:|---:|---|
| **[Claude Opus 4.8 · adaptive/max](https://www.anthropic.com/news/claude-opus-4-8)** | NR | NR | **88.6** | **74.6 · v2.1** |
| [Devstral Small 2](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512#benchmark-results) | NR | NR | **68.0** | **22.5 · v2.0** |
| [Gemma 4 12B IT](https://huggingface.co/google/gemma-4-12B-it#benchmark-results) | NR | **69.0** | NR | NR |
| [Gemma 4 26B A4B IT](https://huggingface.co/google/gemma-4-26B-A4B-it#benchmark-results) | **55.87**¹ | **68.2** | NR | NR |
| [Gemma 4 E4B IT](https://huggingface.co/google/gemma-4-E4B-it#benchmark-results) | **33.92**¹ | **42.2** | NR | NR |
| [GLM-4.7-Flash](https://huggingface.co/zai-org/GLM-4.7-Flash#performances-on-benchmarks) | NR | **79.5** | **59.2** | NR |
| **[GPT-5.3-Codex · xhigh](https://openai.com/index/introducing-gpt-5-3-codex/)** | NR | NR | NR | **77.3 · v2.0** |
| **[GPT-5.6 Sol · OpenAI report](https://openai.com/index/gpt-5-6/)** | NR | NR | NR | **88.8 · v2.1** |
| [gpt-oss-20b · high reasoning](https://deploymentsafety.openai.com/gpt-oss/a2) | **49.88**¹ | NR | **60.7**² | NR |
| [LFM2.5-8B-A1B](https://www.liquid.ai/blog/lfm2-5-8b-a1b) | **48.50**³ | NR | NR | NR |
| [Ministral 3 14B Instruct 2512](https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512) | NR | NR | NR | NR |
| [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B#benchmark-results) | **50.3** | **79.9** | NR | NR |
| [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B#benchmark-results) | **66.1** | **79.1** | NR | NR |
| [Qwen3.8-27B · Terminus](https://huggingface.co/Qwen/Qwen3.8-27B#benchmark-results) | NR | NR | NR | **73.0 · v2.1** |

¹ These BFCL results are **Liquid's evaluations of competing models**, from its [comparison](https://www.liquid.ai/blog/lfm2-5-8b-a1b). They are not scores from the Google/OpenAI evaluations linked for other columns.

² OpenAI's gpt-oss result uses **477 tasks**, while Claude's reported Verified result uses 500. Treat the difference as directional, not a matched experiment.

³ Liquid's launch article reports **48.50**, while its [model card](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B#performance) reports **49.73**. The discrepancy is unresolved. Its τ² Telecom **88.07** and Retail **39.82** are domain scores, not an aggregate.

Gemma's τ² values average three domains. Qwen and Z.ai document different evaluation adjustments; their close scores do not establish equivalent quality. Ministral remains unscored here: a score for its separate **Reasoning** checkpoint must not be assigned to **Instruct**.

Claude's terminal anchor is Anthropic's **74.6**, verified against its [official chart](https://www-cdn.anthropic.com/images/4zrzovbb/website/a9007019094f217e98cb8261a2765d7646c01708-2600x1392.png) and [system card](https://www-cdn.anthropic.com/0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf).

### Cleaner frontier comparison: one evaluator and agent framework

The [DeepSWE v1.1 leaderboard](https://deepswe.datacurve.ai/) uses **113 tasks and mini-swe-agent for all rows below**, as published on 22 September 2026. This provides a stronger reference than mixing vendor headline scores. Values and ± intervals are reproduced as reported.

| Model / reasoning setting | DeepSWE v1.1 score |
|---|---:|
| GPT-6 astra · xhigh | **74 ± 3** |
| GPT-5.6 Sol · max | **73 ± 3** |
| Kimi K3 · max | **69 ± 5** |
| GLM-5.3 · max | **69 ± 3** |
| GLM-5.3-Flash · max | **63 ± 4** |
| Claude Opus 4.8 · max | **59 ± 2** |

Qwen3.8-27B separately reports **42.2** on DeepSWE v1.1 in its [model card](https://huggingface.co/Qwen/Qwen3.8-27B#benchmark-results); it is not an entry in this same-evaluator subset. No defensible “percentage of Claude quality on CPU” follows from these tables.

## 3. Larger self-hosted alternatives

GPU counts follow the linked serving recipes, except the Qwen 2.4T hardware budget. Host CPU/RAM/disk figures are estimates for one replica. These deployment candidates are alphabetical and unranked: the cited publisher benchmarks do not establish measured quality for each proposed serving configuration.

| Model / proposed precision | GPU configuration | Host CPU / RAM / SSD |
|---|---|---|
| [DeepSeek-V4-Pro-0813](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813) · mixed FP4/FP8 | [4× GB300](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813#how-to-run-with-vllm) · ~1,152 GB HBM | 128 vCPU / 1–2 TiB / 2 TB |
| [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) · mixed MXFP4/MXFP8 | [4× GB200](https://recipes.vllm.ai/deepseek-ai/DeepSeek-V4.1-Flash) · 768 GB HBM | 128 vCPU / 1 TiB / 1.5 TB |
| [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) · FP8 | [4× H200](https://recipes.vllm.ai/zai-org/GLM-5.3-Flash) · 564 GB HBM | 64 vCPU / 512 GiB / 1 TB |
| [GLM-5.3](https://huggingface.co/zai-org/GLM-5.3) · FP8 | [8× H200](https://recipes.vllm.ai/zai-org/GLM-5.3) · 1,128 GB HBM | 128 vCPU / 1–2 TiB / 2 TB |
| [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3) · MXFP4 | [≥8× GB300](https://recipes.vllm.ai/moonshotai/Kimi-K3) · ~2.3 TB HBM | 192–256 vCPU / 2–4 TiB / 4 TB |
| [MiniMax M3](https://huggingface.co/MiniMaxAI/MiniMax-M3) · BF16 | [8× H200](https://recipes.vllm.ai/MiniMaxAI/MiniMax-M3) · 1,128 GB HBM | 128 vCPU / 1–2 TiB / 2 TB |
| [Qwen3.8-2.4T-A95B](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) · official FP8 | [TP16 recipe](https://recipes.vllm.ai/Qwen/Qwen3.8-2.4T-A95B); estimate 16× B300 · ~4.6 TB HBM | 256 vCPU / 4–8 TiB / 6 TB |
| [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) · BF16 | [2× GB300](https://recipes.vllm.ai/Qwen/Qwen3.8-Flash-Next) · ~576 GB HBM | 64 vCPU / 512 GiB / 1 TB |
| [Tencent Hy4-preview](https://huggingface.co/tencent/Hy4-preview) · BF16 | [8× B300](https://recipes.vllm.ai/tencent/Hy4-preview) · ~2.3 TB HBM | 192 vCPU / 2 TiB / 4 TB |

### Publisher benchmark references — not deployment scores

These are **model-publisher reports**, distinct from the shared-evaluator results above and from the proposed serving products. Evaluators/settings differ; alphabetical order is not a quality ranking. **DS = DeepSWE v1.1; TB = Terminal-Bench 2.1.**

| Publisher model reference | Published result |
|---|---|
| [DeepSeek-V4-Pro-0813](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813) | DS **62.7**; TB **87.9** |
| [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) | DS **74.2**; TB **90.6** |
| [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) | DS **63.4**; TB **84.3** |
| [GLM-5.3](https://huggingface.co/zai-org/GLM-5.3) | DS **66.9**; TB **88.2** |
| [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3) | DS **67.5**; TB **88.3** |
| [MiniMax M3](https://huggingface.co/MiniMaxAI/MiniMax-M3) | TB **66.0**; OSWorld-Verified **75.2** |
| [Qwen3.8-2.4T-A95B](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) | **NR for exact open checkpoint** |
| [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) | DS **58.7** |
| [Tencent Hy4-preview](https://huggingface.co/tencent/Hy4-preview) | TB **85.4** |

For terminal-heavy work, DeepSeek V4.1 is an initial unrestricted-budget evaluation candidate based on its publisher's TB result; it does not lead the common AA index above. Its TB result falls from **90.6 to 88.0** under a different agent framework in the same card—evidence that model choice alone does not determine success. Its cited serving path is text-only. Qwen's hosted **3.8-Max** results are not assigned to its open 2.4T checkpoint; the AA table uses the separately named **2.4T-A95B** entry as a model reference, not a verified score for our proposed FP8 deployment.

These allocations do not promise maximum advertised context or production concurrency. Kimi recommends multiple nodes for production; MiniMax's cited fit is tight. GPU architecture, compatible kernels and interconnect matter alongside aggregate memory. MoE “active parameters” do not eliminate storage for inactive experts.

## 4. Licence and price

### Self-hosting

The CPU table's **Qwen, Gemma 4, Ministral, Devstral and gpt-oss** checkpoints use Apache-2.0; **GLM-4.7-Flash** uses MIT. These have no per-token model licence fee under their terms. **LFM2.5 is custom-licensed**, with a $10M annual-revenue threshold in its commercial grant; larger companies need applicable commercial terms. [LFM licence](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B/blob/main/LICENSE)

For the larger models: DeepSeek and GLM-5.3-Flash use MIT; Hy4 uses Apache-2.0. The following have material custom conditions:

| Model | Selection-relevant condition; consult full licence |
|---|---|
| [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE) | Separate agreement for specified MaaS businesses above $20M annual revenue; internal-use exceptions and attribution conditions |
| [GLM-5.3](https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE) | Security review for qualifying MaaS businesses above $10B annual revenue |
| [Qwen Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/main/LICENSE) | Separate licence for MaaS/AI-work-assistant businesses; internal-use exception |
| [Qwen 2.4T](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/blob/main/LICENSE) | Separate licence for specified MaaS/assistant businesses above $50M annual revenue; internal-use exception |
| [MiniMax M3](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/LICENSE) | Commercial notice; prior written authorisation above $20M product/service annual revenue |

### Hosted API price references

**USD per million tokens**, checked on the snapshot date. Input is uncached input. Hosted checkpoints/settings can differ from self-hosted versions.

| Provider/model | Input / cached input / output |
|---|---|
| [DeepSeek V4.1-Flash](https://api-docs.deepseek.com/quick_start/pricing/) | Off-peak **$0.15 / $0.003 / $0.60**; peak **$0.30 / $0.006 / $1.20** |
| [DeepSeek V4-Pro-0813](https://api-docs.deepseek.com/quick_start/pricing/) | Off-peak **$0.66 / $0.022 / $1.98**; peak **$1.32 / $0.044 / $3.96** |
| [Kimi K3](https://platform.kimi.ai/) | **$3.00 / $0.30 / $15.00**; cache writing separately $3.00 |
| [GLM-5.3 / GLM-5.3-Flash](https://docs.z.ai/guides/overview/pricing) | **$1.40 / $0.26 / $4.40**; Flash **$0.15 / $0.03 / $0.50** |
| [MiniMax M3 standard](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise) | ≤512K context **$0.30 / $0.06 / $1.20**; >512K–1M **$0.60 / $0.12 / $2.40** |

Exact hosted prices for the remaining checkpoints were not verified. DeepSeek's peak windows are weekdays 01:00–04:00 and 06:00–10:00 UTC. Tool fees, taxes and commercial licence quotes are additional.

Self-hosting cost depends on utilisation. For scale, [Lambda](https://lambda.ai/pricing) lists **$4.29/hour** for one H100 SXM and **$53.52/hour** for an eight-B200 instance: approximately **$3,132** and **$39,070** per 730-hour month. These are reference bundles, not quotes for the configurations above. CPU-only removes GPU rental, but retries and long task runtimes still cost money.

## 5. CPU-only starting command and acceptance checks

Install a model-compatible [llama.cpp build](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) first, with `llama-server` on your PATH. This example downloads the resource-fit candidate's selected weights when run:

```sh
llama-server \
  -hf unsloth/Qwen3.5-9B-GGUF \
  -hff Qwen3.5-9B-Q4_K_M.gguf \
  --device none --n-gpu-layers 0 \
  --no-op-offload --no-kv-offload --no-mmproj \
  --ctx-size 4096 --parallel 1 --threads 8 --cache-ram 0 \
  --jinja --host 127.0.0.1
```

These [server options](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) disable GPU offloading, the multimodal projector and extra prompt caching. A CPU-only runtime build is also supported. Use the correct [tool-call template](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md); some formats, such as gpt-oss Harmony, need model-specific handling.

Before choosing a model, run the **same tasks, controller, tool permissions and declared context/output/time budgets** against each exact artifact and a named hosted reference. Record artifact revision/hash, runtime version, hardware, cache precision, supported chat/tool template, reasoning settings and any unavoidable differences. A short-context CPU comparison is a workload test, not a reproduction of the AA index. Measure verified completion rate, valid tool calls/retries, median/p95 task time, peak RAM and cost per successful task. Include a tool timeout/recovery case. Loading weights or answering a chat prompt does not prove an agent loop works.

**Verification:** the common-score update checked evaluator model pages, model-specific estimate labels and the v4.3.2 methodology; score/evidence columns, descending reference-score ordering, unique CPU rows and coverage counts were checked locally. One CPU table combines AA references, related writing results, unmeasured local-workflow scores, downloads, hardware and selection notes. Its exact-artifact score boundaries remain explicit. Larger serving configurations remain separated from publisher benchmark references. Earlier primary-source benchmarks, quantised-file sizes and runtime CLI flags retain their stated snapshot. **No local model inference, CPU benchmark, load test or deployment was performed.** RAM estimates and quantised-model quality remain to be measured. Maintain this report using the shared [AI model comparison skill](../custom/skills/ai-model-comparison/SKILL.md).
