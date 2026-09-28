# Memory tools: measured central-library comparison

Verified 28 September 2026 using the AI model comparison skill, an independent
Performance Benchmarker reviewer, and a separate QMD/HTTP test agent. This is a
bounded regression experiment on our reviewed library, not a general memory
benchmark or a production-readiness certification.

**Decision, 28 September 2026:** use Hindsight as the shared memory service.
Basic Memory and QMD were removed from this machine at the user's request to avoid
overlapping tools, including their isolated test runtimes and indexes. The results
below preserve the tested configurations and findings as historical evidence;
they do not describe currently installed alternatives. Reintroducing either tool
requires an explicit decision, not routine setup or refresh.

## CLI versus server

A CLI is an entry point. Basic Memory and QMD both run MCP server processes when
launched with `mcp`; stdio lets an AI client manage a local subprocess, while HTTP
allows a persistent shared endpoint. Their local indexes use SQLite. We verified
both stdio and temporary loopback HTTP connections.

Hindsight uses a backend and PostgreSQL. It also supports local launches and
embedded PostgreSQL for development; it does not require a remote cloud service.
This user's configured connection points to an existing remote bank. The tested
MCP server identified itself as 0.10.1. No Hindsight executable or named container
was found in the checked local binary/tool locations and running-container list;
this is not an exhaustive filesystem audit. See [Hindsight installation](https://hindsight.vectorize.io/developer/installation),
[Basic Memory CLI](https://docs.basicmemory.com/reference/cli-reference), and
[QMD transports](https://github.com/tobi/qmd#http-transport).

Any of these tools needs a running service somewhere to provide one shared remote
library. Separate local indexes need file distribution; MCP does not sync Git.

## One canonical measured selection table

Score = **10 × expected-source hits within the first three distinct sources / 14**.
Sorted by score descending, then first-place hits descending. All counts repeated
identically across three trials. This measures source discovery, not completed
engineering tasks, full-answer correctness, or how often agents choose to recall.
Earlier documentation-based scores of 10/8/6 counted product capabilities and
must not be interpreted as these measured retrieval scores.

| Tested product/configuration | Source-finding score /10 | Top-three hits | First-place hits | Median / p95 request latency | Decision |
| --- | ---: | ---: | ---: | --- | --- |
| Hindsight 0.10.1, existing remote bank, chunks-only, no reflection/consolidation/reranking | **10.0** | 14/14 | 12/14 | 1.262 s / 1.834 s | Keep the working central bank; more expected sources ranked first here. Explicit reviewed ingestion remains necessary. |
| Basic Memory 0.23.2, isolated Homebrew Python 3.14.3, SQLite, local BGE-small-en-v1.5 embeddings, hybrid search, no reranker, automatic frontmatter/permalink writes disabled | **10.0** | 14/14 | 10/14 | 27.9 ms / 50.1 ms | Strong file-based alternative. Test runtime and indexing readiness were essential; global installation still needs runtime repair. |
| QMD 2.8.3 (`facd35e`), local embeddingGemma-300M Q8_0, typed lex+vec queries, `rerank:false` | **9.3** | 13/14 | 11/14 | 11.4 ms / 15.0 ms | Useful read-only document search. Panyora artifact-identity source ranked eighth; requires explicit index/embedding updates. |

Latency includes the MCP request and response, using persistent connections and
42 calls per candidate. p95 uses nearest-rank selection. First requests were
0.992 s Hindsight, 0.504 s Basic Memory, and 1.174 s QMD. The local machine is an
Apple M4 Pro, 14 physical cores, 48 GiB RAM. Remote hardware and embedding identity
were not established through MCP. Local cache effects, different models and remote
network/service time prevent hardware-efficiency or scalability conclusions.

## What was actually tested

The corpus contains the nine reviewed cases and five navigation summaries listed
in [the reviewed index](HINDSIGHT_LIBRARY.json). MCP `get_document` supplied the
exact stored Hindsight payloads; both local tools received those same bytes.
The 14 existing questions were fixed before queries ran. Three repetitions test
stability, not 42 independent quality cases. Sanitized per-query ranks, timings
and corpus hashes are in [the result artifact](tools/memory-comparison-results-2026-09-28.json).

All tools used retrieval, not answer generation. QMD's embeddingGemma is a text
encoder, not a Gemma chat/reasoning run. Local test processes received no provider
credentials. Hindsight used the configured MCP connection and its existing gateway
transport authentication; no model-provider key or direct REST call was used.
The existing chunks-only configuration was reasserted through MCP, but server-side
provider traces were not independently audited.

Basic Memory used `search_notes(search_type="hybrid", page_size=20,
output_format="json")`; QMD used the same question as explicit lex and vec searches,
limit 20, reranking disabled. Hindsight recall used budget high and max_tokens 5000,
restricted to reviewed tags. Native chunking, candidate ranking and response
budgets differ. We deduplicated ranked source paths and scored the first three;
this is an integration comparison, not a controlled algorithm/model experiment.

The independent reviewer found substantive supporting passages in Hindsight and
Basic Memory results for all 14 questions. Basic Memory returns body excerpts and
matched chunks, not necessarily complete files. Some QMD snippets were headers or
partial context; agents need `get` before reasoning. All 14 QMD `get` and Basic
Memory `read_note` readbacks matched the input payloads. A separate absent-topic
question returned unrelated material from all three. Scores such as 1.0 or 100%
were ranking values, not confidence that the requested fact exists.

## Installation and lifecycle findings

Basic Memory's original global installation used python.org Python 3.12.8 without
SQLite extension-loading support. Semantic searches failed, even though MCP's
`is_error` flag was false. Those failures are availability defects, not a zero
retrieval-quality score. The same Basic Memory version was installed in an
isolated test environment using Homebrew Python 3.14.3; global tool/configuration
files were not replaced. The original global command therefore remains unrepaired.

MCP initialization also preceded completion of Basic Memory's background indexing.
Early runs were discarded. The scored run followed explicit `reindex --full`,
which reported 14 observed/indexed/embedded entities and zero errors. Indexing and
embedding then took 4.72 s with its model already cached. Basic Memory's default
indexing added frontmatter to test copies. Setting `ensure_frontmatter_on_sync=false`
and `disable_permalinks=true` preserved all 14 original payload hashes.

Basic Memory MCP writes materialized Markdown asynchronously. After waiting for
the actual file, a disposable fixture's external edit, rename and deletion updated
lexical search automatically in about 0.56, 0.53 and 0.52 seconds, respectively.
The old edit text disappeared; the renamed file had one result at its new path.
All fixture files were removed. These checks do not establish semantic embedding
freshness, case-only/Unicode rename behavior, or concurrent-writer correctness.

QMD initially had no collections. Its isolated index embedded 14 documents into
43 chunks in 30.05 s including the local model preparation. Only the 333,590,944-byte
embedding model was downloaded, not generation/reranker models. Its SHA-256 is
`b5ce9d77a3fc4b3b39ccb5643c36777911cc4eb46a66962eadfa3f5f60490d63`.
Fixture adds/edits/renames/deletes stayed stale during three-second observation
windows, then reconciled after `qmd update`. These were lexical checks; changed
semantic content additionally needs `qmd embed`. Its MCP tools are read-only.

Hindsight's disposable MCP write/update/delete test passed: exact readback,
retrieval of replacement content, absence of superseded text, and no results after
deletion. The bank returned to 14 reviewed documents. No file watcher was added.

Temporary localhost HTTP tests passed for both local tools and their child servers
were stopped. Remote authentication/TLS, Windows/Linux execution, multi-client
concurrency, sustained load, peak resource usage and a fresh Claude consumer session
were not tested. No production services were restarted or global MCP registrations
changed. Merely installing either CLI does not connect it to Claude/Codex.

## Recommendation and reusable acceptance gates

Keep Hindsight while deciding whether Basic Memory's file ownership and automatic
local indexing justify migration. Both passed this small source-discovery set;
the result does not establish equivalent general quality. QMD is a useful search
companion, but adding every tool would create more operational work and overlapping
retrieval choices. None automatically distributes approved Git changes to a remote
host or guarantees that agents search before acting.

For any migration: preserve source bytes unless changes are explicitly reviewed;
wait for complete indexing/embeddings rather than MCP readiness; inspect tool
payloads for failures; verify source/passage relevance and reject unrelated hits;
test edit/delete/rename across both lexical and semantic retrieval; then verify
authenticated access and concurrent writers. Keep app-specific documents with
their owners and index only authorized reviewed material.
