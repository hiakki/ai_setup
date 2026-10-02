# Shared Hindsight memory through a gateway

For measured local alternatives, CLI/server behavior and the common scored test,
see [Memory tool comparison](MEMORY_COMPARISON.md).

Hindsight is an optional remote MCP connection for Claude Code and Codex. The
`hindsight` component registers both clients at user scope and adds shared usage
guidance. It works through the same Python installer on macOS, Ubuntu/Debian and
native Windows. It does not install a server, change a gateway, ingest documents,
capture sessions or enable scheduled refreshes. Remote hosting and the server's
model configuration remain the endpoint operator's responsibility.

## Configure once per machine

Supply the complete bank MCP URL in `HINDSIGHT_MCP_URL`, for example
`https://your-gateway.example/hindsight/mcp/your-bank/`. This is the memory MCP
route, not the gateway's `/v1/chat/completions` route. The installer requires
HTTPS except for loopback development and rejects credentials, query parameters
and fragments in the URL. No personal endpoint or bank is embedded in this repo.

The credential reference defaults to `LLM_GATEWAY_KEY`. Set
`HINDSIGHT_MCP_TOKEN_ENV` to a different variable name if needed. Provision that
variable through your normal secret manager or private shell environment before
starting clients; the installer never copies its value into client configuration
or installer state. A Git-ignored project `.env` is **not automatically loaded**
by Claude/Codex. Clients launched from an IDE/desktop also need the variable in
their own launch environment, not only in an unrelated terminal.

macOS / Ubuntu / Debian, from the checkout:

```sh
export HINDSIGHT_MCP_URL='https://your-gateway.example/hindsight/mcp/your-bank/'
bash install.sh install --only hindsight,docs,hub
# For a fresh full setup, select --only all,hindsight instead.
```

Native Windows PowerShell:

```powershell
$env:HINDSIGHT_MCP_URL = 'https://your-gateway.example/hindsight/mcp/your-bank/'
.\install.ps1 -Only 'hindsight,docs,hub'
# For a fresh full setup, select -Only 'all,hindsight' instead.
```

An existing installation can also use its Python directly with
`setup.py install --only hindsight,docs,hub`; this avoids repeating prerequisite
bootstrap. Configure credentials separately on every machine. Registration can
complete before a key is provisioned; that does not establish a working connection.

## Client configuration and preservation

Claude's user-level `~/.claude.json` entry uses HTTP transport and the literal
header template `Bearer ${LLM_GATEWAY_KEY}`. Preserve those dollar-sign/braces when
passing JSON or a CLI argument: single quotes in Bash and PowerShell prevent the
shell from substituting the key into persistent configuration.

Codex's `~/.codex/config.toml` entry uses:

```toml
[mcp_servers.hindsight]
url = "https://your-gateway.example/hindsight/mcp/your-bank/"
bearer_token_env_var = "LLM_GATEWAY_KEY"
```

The installer preserves other MCP servers and existing Hindsight settings,
including credentials, custom transport and intentional disablement. A supplied
URL conflicting with an existing registration fails before either client is
changed. Deliberate bank/credential changes require reviewing those existing
settings; rerunning is not an overwrite switch. Later reruns/updates can omit
`HINDSIGHT_MCP_URL` once both registrations exist. Shared updates refresh guidance
only for installations that already selected Hindsight. Ordinary `all` does not
activate this optional connection for other users.

## Verify the actual connection

Start a fresh client with the token environment variable available. In Claude,
use `/mcp` to inspect Hindsight. `codex mcp get hindsight` confirms registration;
it is not a live authentication test. Project-level or managed configuration may
override a user-level server of the same name, so check the active client too.

`setup.py verify` checks registration and managed guidance locally. The optional
`python tests/check_hindsight.py` command checks both client configuration shapes,
then performs an authenticated MCP initialize and tool listing against their
shared endpoint. It reads the key from the process environment, refuses redirects
and reports only connection/tool metadata. It does not retain, recall, reflect,
read stored memories or trigger model inference. Run it only for an endpoint you
are authorized to access. Windows uses the same command with its installed Python.

A successful handshake/tool list does not validate extraction, semantic retrieval,
source attribution, bank authorization or model quality. Those need a separate
approved-content pilot. The current agent session may need to be reopened before
it discovers a newly registered server; no application/service restart is needed.

## Knowledge ownership

### Claude/Codex reasoning with MCP retrieval

For client-led reasoning, Claude Code or Codex reads the installed skills, agent
definitions and canonical discussion/case files, writes the reviewed lesson, and
produces the final answer. Hindsight supplies searchable evidence through MCP.
It does not replace the client model or execute a SKILL.md as an agent.

Use the clients' existing account logins. No model-provider API key needs to be
given to Hindsight for this retrieval-only workflow. An authenticated gateway can
still require its bearer token on the MCP connection; transport authentication is
different from paying a model provider. Use MCP tools rather than direct REST
calls for this workflow. Do not copy Claude/Codex login tokens to the server.

Ordinary Hindsight `retain` can invoke its configured LLM for extraction, and
`reflect` generates an answer with that server-side model. Avoiding `reflect`
alone therefore does not remove the LLM dependency. For an authorized bank, use
MCP `update_bank` with this `config_updates` profile before retaining any content:

```json
{
  "retain_extraction_mode": "chunks",
  "enable_observations": false,
  "enable_auto_consolidation": false,
  "enable_temporal_retrieval": false,
  "enable_graph_retrieval": false,
  "enable_reranking": false,
  "mcp_enabled_tools": [
    "retain", "sync_retain", "recall", "list_memories", "get_memory",
    "list_documents", "get_document", "delete_document", "list_operations",
    "get_operation", "cancel_operation", "list_tags", "get_bank", "update_bank"
  ]
}
```

Review existing bank settings first. Named retain strategies can override chunks
mode; do not select one that enables extraction. This profile still uses embeddings
and keyword search; it does not mean model-free computation or necessarily offline
execution. Reflection, generated knowledge pages and model-based consolidation
are intentionally unavailable through this bank's MCP tool allowlist. An operator
can change the bank configuration later, so this is not an immutable access policy.
The installer registers clients but does not silently configure remote banks.

After recall, check relevance and source freshness, open the canonical file, and
apply the relevant installed skill. Similarity scores are not factual confidence.
Retain small reviewed summaries with stable document IDs, source path, source hash,
revision or explicit working-tree status, review date and evidence limits. Replace
the same document ID for a correction and verify that old text is no longer
recalled. Keep historical reasoning in the canonical Git document. Never interpret
a successful MCP handshake as proof that the selected bank exists or has content.

### Initial bounded live verification — 28 September 2026

This initial three-summary pilot is retained as history. The reviewed library
expansion below supersedes its coverage counts and unindexed-audio observation.

On the tested Hindsight 0.10.1 deployment, the selected MCP endpoint authenticated
while its new bank did not yet exist. MCP `update_bank` established the bank and
the retrieval-only profile before ingestion. Three sanitized lesson summaries
were retained from the central Panyora, DelX and bulkBuyer cases; full app docs,
transcripts, skill libraries and credentials were not ingested.

| Check | Observed result | Limit |
| --- | --- | --- |
| Synchronous retention and source metadata | Three lessons stored and returned with canonical path, SHA-256, checkout revision and working-tree status | Three reviewed summaries, not complete library ingestion |
| Paraphrased retrieval after all three lessons were indexed | Expected lesson ranked first for all three questions | Tiny corpus; not a general retrieval-quality benchmark |
| Follow-up discovery comparison | Three new paraphrases retrieved the expected lesson first; full-question literal search missed all three, while targeted keyword search found all three canonical cases | Hindsight reduces dependence on matching vocabulary; this does not prove superiority over an agent that reformulates file searches |
| Lesson present only in files | The audio acceptance question returned unrelated memories; keyword search found the central native-audio case | Only three summaries are indexed; memory does not cover the full library |
| Correction | Reusing a disposable document ID replaced its previous text; recall returned one current version | No generated knowledge pages were involved |
| Deletion | Disposable test document removed; scoped recall returned no results | The three useful reviewed lessons remain |
| Unrelated question | All three unrelated candidates were still returned | Client must reject irrelevant evidence; retrieval is not an answer |
| Server-side reflection | MCP invocation rejected by the bank's tool restriction | Operators can later change the restriction |
| Codex consumer | Fresh read-only CLI run made three MCP recalls, read canonical cases and an installed skill, verified source hashes, and generated source-backed recommendations | Explicit test prompt; does not prove automatic participation in every future task |
| Follow-up new-project decisions | Fresh Codex session used the global discovery workflow, rejected three flawed plans with cited failure mechanisms and target acceptance gates, found the unindexed audio case through file search, and declined to invent a wedding-colour approval | Hypothetical target, explicit discovery request; proposed gates were not executed in an app and no reduction in production incidents was measured |
| Claude consumer | MCP connected; inference did not complete | Initial inherited API key had no credit; retry using the existing Team login returned HTTP 401 from Claude authentication |

Codex's final reasoning came from its configured client model, not Hindsight
reflection. Source hashes matched the files used by that run. The historical case
limits and target-specific verification gates were retained in its answer.
The initial Claude attempt connected to MCP but failed before reasoning because
an inherited provider API key had no credit; this is separate from Hindsight
authentication. Use the existing Claude account login rather than that key.
The Team-login retry removed the API-key/auth-token overrides only from the test
process and reached repeated Claude authentication failures. Refresh the Claude
login interactively, then repeat the consumer test; no provider credentials were
copied into Hindsight and no global Claude authentication settings were changed.

This establishes a useful semantic discovery layer for the existing central files.
It does not establish exhaustive knowledge coverage, automatic file/memory sync,
unattended client credential provisioning, large-corpus precision, or improved
production outcomes. Central publication and other-machine updates remain separate.

### Will this help projects avoid repeating mistakes?

The verified benefit is discovery across different wording: a new app can ask
about a lost provisioning response and find a previously reviewed uncertain-write
lesson without knowing the source project's name. The client must still read the
source, understand its evidence limits, and adapt the regression gate to the target.
The follow-up questions also exposed a coverage gap and irrelevant results; neither
an empty nor a nonempty memory response establishes whether the file library has
relevant evidence. Search both, and reject unrelated matches.

Use the existing [learning workflow](LEARNING_WORKFLOW.md) as a maintained loop:

1. Before a consequential design or fix, search memory and central files. Open
   source files and relevant skills; inspect current owner docs when needed.
2. State the previous failure mechanism, the adopt/adapt/reject decision and a
   target-specific test that would catch the same mistake. Put target facts and
   actual test results in the app's docs.
3. After verification, amend the canonical reusable case or skill. Review a small
   sanitized summary for memory, preserving source identity and evidence limits.
4. Replace or remove stale memory deliberately and test recall after the change.
   A changed source hash requires review; it is not automatically synchronized.

Hindsight adds semantic discovery to this loop. Claude/Codex provides reasoning;
the maintained files provide authority; application tests establish whether the
mistake was actually prevented. Neither memory nor instructions train model weights
or guarantee compliance. See [learning coverage](LEARNING_COVERAGE.md) for the
remaining historical backlog. Existing machines need a working client session;
new machines also need the central setup and authorized access to the shared bank.

### Reviewed library expansion — 28 September 2026

The [reviewed memory index](HINDSIGHT_LIBRARY.json) identifies **14 stable bank
document IDs**: all nine central case documents and five concise navigation
entries. The original three pilot IDs were replaced in place with their complete
reviewed case content. No duplicate pilot summaries were retained. Hindsight
split these documents into **119 memory units**; this is a chunk count, not a
count of independent lessons or proof of semantic completeness.

The case scope is Panyora, Elvique, Servinoza, NarrateAI, bulkBuyer, DelX,
card-savvy, infrastructure cost/drift, and native audio. These are already
sanitized central cases, including later dated corrections and evidence limits.
Private application documents and conversations were not fetched or uploaded.
Navigation entries point to the case catalog, current-project documentation
catalog, engineering playbook, learning workflow and global skills guide.
Skill/agent implementations remain in their canonical locations or with their
original providers; memory provides navigation, not another agent library.

The expansion used MCP `update_bank`, `sync_retain`, `get_document`,
`list_documents` and paginated `list_memories`. The non-generative chunks profile
was explicitly preserved, including clearing extraction-strategy overrides.
Every retained document was read back and compared with its submitted text and
source metadata. All 14 source hashes still matched at completion; all 41 unique
local file-link targets in the source documents existed. Relative links resolve
from the canonical source file's parent. Owner-relative private app pointers
still require authorized source access; their current remote state was not audited.

The 14 stored retrieval questions each returned their expected source within the
first three distinct source documents: 12 ranked first, bulkBuyer second and the
engineering playbook third. Returned passages were inspected for relevance and
evidence limits. These are source-discovery checks on this snapshot, not a
general retrieval benchmark or proof that every lesson will be recalled.

### Servinoza reviewed resynchronization — 2 October 2026

The existing `ai-setup-case-servinoza` document was replaced in place from merged
central revision `03e1b66c65d2a2f5d1b0d387fe7937f354ad3439`; no second Servinoza
document was created. Before retention, the bank was reset to the chunks-only
profile described above. MCP `sync_retain` produced 55 memory units. MCP
`get_document` then matched the submitted source bytes, SHA-256
`3ac0fadad94367e1393a6dc6d0ce36ca89caea95a6a9a027d27a0871ae7e1d7a` and source
metadata. A new query about a failed retryable payment and its release-blocking
test recalled the payment-state and hosted-gate lesson. This verifies one reviewed
document update and query, not the freshness of every indexed document or a real
provider payment.

#### Maintain the reviewed index through MCP

The JSON index ships with the normal cross-platform `docs` component. It contains
source-relative paths, reviewed hashes, stable IDs, navigation text and retrieval
questions; no personal gateway endpoint or credential. It is a review snapshot,
not a scheduled synchronization job or an install-time upload instruction.

1. Re-read changed sources and privacy/evidence limits before updating their
   `reviewed_sha256`. A mismatched hash means pending review, not permission to
   silently accept the new bytes. Review new cases before extending the index.
2. For `reviewed_document`, retain the complete reviewed central case. For
   `reviewed_pointer`, retain its reviewed `summary` and canonical source path.
   Include source project/path/hash, checkout revision, explicit working-tree
   status, review date and entry mode in metadata. Preserve the stable document ID.
3. Use the authorized client's MCP `sync_retain` only after establishing the
   chunks-only profile. Never fall back to model extraction or direct REST calls.
4. Read back with `get_document`; verify content, metadata and current source hash.
   Paginate `list_memories` to check all chunks. Compare the explicit index against
   the case catalog, not just the number of memories. Do not delete unrelated bank
   entries or assume a partial list is exhaustive.
5. Run the stored questions with MCP `recall`, check the relevant source and its
   evidence limits, and test new failure mechanisms. A pointer hit alone does not
   prove the right passage was retrieved or that a project applied it correctly.

This closes the audited **nine-case/five-pointer** gap. It does not close the
historical review backlog in [learning coverage](LEARNING_COVERAGE.md), copy every
skill into memory, publish the local checkout or update other machines. Later
source changes require another reviewed memory update. Git remains canonical.

Use Hindsight recall alongside `ai-setup search`; verify important claims against
their original files and evidence. Git remains authoritative for skills, agents,
rules and reviewed shared lessons. Current architecture, crons, CI/CD and release
evidence remain with each application. A memory write does not contribute to Git.

Retain only reviewed, reusable, sanitized material within the task's authorization,
with source project/path/revision, date, status and evidence limits. Do not dump
private source, transcripts, credentials or customer records into a shared bank.
Bank names are not an access-control policy. On corrections/deletions, verify both
facts and generated knowledge pages: deletion alone may not mark pages stale.
When memory is unavailable, keep using the file library and report the limitation.

Provider references: [Hindsight MCP](https://hindsight.vectorize.io/developer/mcp-server),
[mental-model freshness](https://hindsight.vectorize.io/developer/api/mental-models),
[Claude MCP](https://code.claude.com/docs/en/mcp),
[Codex MCP](https://developers.openai.com/codex/mcp).
