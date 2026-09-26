# Agentic AI models: CPU-only choices, benchmark scores and cost

**Updated 26 September 2026.** For a **32 GB RAM machine with no GPU**, start by evaluating **Qwen3.5-9B Q4_K_M**: approximately **5.68 GB of weights, 12–18 GB total RAM, 8 vCPU, 0 GB VRAM**. It combines memory headroom with published tool-use results. This is a recommendation for evaluation, not a locally measured performance claim.

An agent needs both a model and software that executes its tools. The tables compare models; LiteLLM can provide the gateway, while an agent controller manages tool execution and state. The separate [decision-model comparison](DECISION_AI_MODELS.md) covers specialist decision engines.

## 1. Models for 32 GB RAM — no GPU required

**These are CPU-only configurations; a GPU is not required.** Use a compatible [llama.cpp](https://github.com/ggml-org/llama.cpp) build and the linked quantisation, rather than the original BF16 weights. Model/runtime compatibility and peak RAM still need verification on your machine.

RAM figures are **planning estimates for the whole machine**, including weights, inference buffers/cache and 4–6 GB for a lean OS and controller. Assumptions: **text only, 4,096 total context tokens, one active request, no additional prompt-cache allocation**. Browsers, builds and other services need separate headroom. A 32 GB machine has approximately 29.8 GiB.

| Model | Quantised download / weight size | Total RAM estimate | CPU estimate | GPU required |
|---|---|---:|---:|---|
| **Qwen3.5-9B — first choice** | [Q4_K_M · 5.68 GB](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) | **12–18 GB** | 8 vCPU | **None · 0 GB VRAM** |
| Qwen3.5-4B | [Q4_K_M · 2.74 GB](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) | 8–12 GB | 4–8 vCPU | **None · 0 GB VRAM** |
| Gemma 4 E4B IT | [Q4_0 · 4.59 GB](https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF) | 10–16 GB | 4–8 vCPU | **None · 0 GB VRAM** |
| Gemma 4 12B IT | [Q4_0 · 7.22 GB](https://huggingface.co/ggml-org/gemma-4-12B-it-GGUF) | 14–20 GB | 8–12 vCPU | **None · 0 GB VRAM** |
| LFM2.5-8B-A1B | [Q4_K_M · 5.16 GB](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-GGUF) | 10–16 GB | 4–8 vCPU | **None · 0 GB VRAM** |
| Ministral 3 14B Instruct 2512 | [Q4_K_M · 8.24 GB](https://huggingface.co/unsloth/Ministral-3-14B-Instruct-2512-GGUF) | 16–24 GB | 8–12 vCPU | **None · 0 GB VRAM** |
| gpt-oss-20b | [MXFP4 · 12.11 GB](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF) | 18–26 GB | 8–16 vCPU | **None · 0 GB VRAM** |
| Devstral Small 2 24B Instruct 2512 | [Q4_K_M · 14.33 GB](https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF) | 22–30 GB | 8–16 vCPU | **None · 0 GB VRAM** |
| Gemma 4 26B A4B IT | [Q4_0 · 14.62 GB](https://huggingface.co/ggml-org/gemma-4-26B-A4B-it-GGUF) | 22–30 GB | 8–16 vCPU | **None · 0 GB VRAM** |
| GLM-4.7-Flash | [Q4_K_M · 18.31 GB](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF) | 26–30 GB | 8–16 vCPU | **None · 0 GB VRAM** |
| Qwen3.8-27B | [UD-Q4_K_M · 16.46 GB](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) | 24–30 GB | 12–16 vCPU | **None · 0 GB VRAM** |

Reserve 30–50 GB SSD for a smaller candidate, or 50–80 GB for a larger one. The final four entries have little spare RAM; start at 4K context and measure peak usage. Do not count swapping as a successful fit. CPU memory bandwidth affects speed, and dense 24–27B models can be slow despite fitting. No CPU tokens/second or task latency was measured here.

## 2. Scores, including Codex and Claude references

**Scores are published percentages; higher is better.** They describe the evaluated model and agent setup, **not a measured score for the CPU quantisations above**. Different tasks cannot be averaged into a meaningful universal “agent score”.

- **BFCL v4:** function/tool calling.
- **τ²-bench:** multi-turn support workflows; aggregate and individual-domain scores are distinct.
- **SWE-bench Verified:** fixing real repository issues.
- **Terminal-Bench:** terminal tasks; **2.0 and 2.1 are different benchmarks**.
- **DeepSWE v1.1:** repository-level engineering tasks.

**NR** means no matching result was established in the cited sources, not zero. “Codex” names a product: reference rows therefore specify its underlying model.

### Small-model results and larger-model anchors

Rows with BFCL v4 evidence are sorted by that score; remaining models use other evidence. Evaluators and settings differ, so this is not a controlled overall ranking.

| Model / evaluation setting | BFCL v4 | τ²-bench aggregate | SWE-bench Verified | Terminal-Bench |
|---|---:|---:|---:|---|
| [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B#benchmark-results) | **66.1** | **79.1** | NR | NR |
| [Gemma 4 26B A4B IT](https://huggingface.co/google/gemma-4-26B-A4B-it#benchmark-results) | **55.87**¹ | **68.2** | NR | NR |
| [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B#benchmark-results) | **50.3** | **79.9** | NR | NR |
| [gpt-oss-20b · high reasoning](https://deploymentsafety.openai.com/gpt-oss/a2) | **49.88**¹ | NR | **60.7**² | NR |
| [LFM2.5-8B-A1B](https://www.liquid.ai/blog/lfm2-5-8b-a1b) | **48.50**³ | NR | NR | NR |
| [Gemma 4 E4B IT](https://huggingface.co/google/gemma-4-E4B-it#benchmark-results) | **33.92**¹ | **42.2** | NR | NR |
| [Gemma 4 12B IT](https://huggingface.co/google/gemma-4-12B-it#benchmark-results) | NR | **69.0** | NR | NR |
| [Devstral Small 2](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512#benchmark-results) | NR | NR | **68.0** | **22.5 · v2.0** |
| [GLM-4.7-Flash](https://huggingface.co/zai-org/GLM-4.7-Flash#performances-on-benchmarks) | NR | **79.5** | **59.2** | NR |
| [Qwen3.8-27B · Terminus](https://huggingface.co/Qwen/Qwen3.8-27B#benchmark-results) | NR | NR | NR | **73.0 · v2.1** |
| [Ministral 3 14B Instruct 2512](https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512) | NR | NR | NR | NR |
| **[GPT-5.3-Codex · xhigh](https://openai.com/index/introducing-gpt-5-3-codex/)** | NR | NR | NR | **77.3 · v2.0** |
| **[GPT-5.6 Sol · OpenAI report](https://openai.com/index/gpt-5-6/)** | NR | NR | NR | **88.8 · v2.1** |
| **[Claude Opus 4.8 · adaptive/max](https://www.anthropic.com/news/claude-opus-4-8)** | NR | NR | **88.6** | **74.6 · v2.1** |

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

Scores here are **model-publisher reports**, distinct from the shared-evaluator table above. **DS = DeepSWE v1.1; TB = Terminal-Bench 2.1.** GPU counts follow the linked serving recipes, except the Qwen 2.4T hardware budget. Host CPU/RAM/disk figures are estimates for one replica.

| Model / precision | Published score | GPU configuration | Host CPU / RAM / SSD |
|---|---|---|---|
| [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) · mixed MXFP4/MXFP8 | DS **74.2**; TB **90.6** | [4× GB200](https://recipes.vllm.ai/deepseek-ai/DeepSeek-V4.1-Flash) · 768 GB HBM | 128 vCPU / 1 TiB / 1.5 TB |
| [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3) · MXFP4 | DS **67.5**; TB **88.3** | [≥8× GB300](https://recipes.vllm.ai/moonshotai/Kimi-K3) · ~2.3 TB HBM | 192–256 vCPU / 2–4 TiB / 4 TB |
| [GLM-5.3](https://huggingface.co/zai-org/GLM-5.3) · FP8 | DS **66.9**; TB **88.2** | [8× H200](https://recipes.vllm.ai/zai-org/GLM-5.3) · 1,128 GB HBM | 128 vCPU / 1–2 TiB / 2 TB |
| [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) · FP8 | DS **63.4**; TB **84.3** | [4× H200](https://recipes.vllm.ai/zai-org/GLM-5.3-Flash) · 564 GB HBM | 64 vCPU / 512 GiB / 1 TB |
| [DeepSeek-V4-Pro-0813](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813) · mixed FP4/FP8 | DS **62.7**; TB **87.9** | [4× GB300](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813#how-to-run-with-vllm) · ~1,152 GB HBM | 128 vCPU / 1–2 TiB / 2 TB |
| [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) · BF16 | DS **58.7** | [2× GB300](https://recipes.vllm.ai/Qwen/Qwen3.8-Flash-Next) · ~576 GB HBM | 64 vCPU / 512 GiB / 1 TB |
| [Tencent Hy4-preview](https://huggingface.co/tencent/Hy4-preview) · BF16 | TB **85.4** | [8× B300](https://recipes.vllm.ai/tencent/Hy4-preview) · ~2.3 TB HBM | 192 vCPU / 2 TiB / 4 TB |
| [MiniMax M3](https://huggingface.co/MiniMaxAI/MiniMax-M3) · BF16 | TB **66.0**; OSWorld-Verified **75.2** | [8× H200](https://recipes.vllm.ai/MiniMaxAI/MiniMax-M3) · 1,128 GB HBM | 128 vCPU / 1–2 TiB / 2 TB |
| [Qwen3.8-2.4T-A95B](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) · official FP8 | **NR for exact open checkpoint** | [TP16 recipe](https://recipes.vllm.ai/Qwen/Qwen3.8-2.4T-A95B); estimate 16× B300 · ~4.6 TB HBM | 256 vCPU / 4–8 TiB / 6 TB |

DeepSeek V4.1 is the initial unrestricted-budget evaluation choice. Its TB result falls from **90.6 to 88.0** under a different agent framework in the same card—evidence that model choice alone does not determine success. Its cited serving path is text-only. Qwen's hosted **3.8-Max** results are not assigned to its open 2.4T checkpoint.

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

Install a model-compatible [llama.cpp build](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) first, with `llama-server` on your PATH. This example downloads the recommended model's selected weights when run:

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

Before choosing a model, run the **same tasks and tool permissions** against it and a named hosted reference. Measure verified completion rate, valid tool calls/retries, median/p95 task time, peak RAM and cost per successful task. Include a tool timeout/recovery case. Loading weights or answering a chat prompt does not prove an agent loop works.

**Verification:** primary-source benchmarks, quantised-file sizes and runtime CLI flags were checked. **No local model inference, CPU benchmark, load test or deployment was performed.** RAM estimates and quantised-model quality remain to be measured.
