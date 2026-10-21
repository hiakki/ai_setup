# Shared developer knowledge with Entire and Agent Wiki

This setup separates raw evidence, collaborative proposals and approved reusable
knowledge. It does not treat an agent transcript or Wiki edit as an approved fact.

```text
Claude/Codex session
       │ automatic after repository opt-in
       ▼
Entire checkpoint in a private, project-scoped Git remote
       │ reviewed and sanitized proposal
       ▼
Agent Wiki proposal + comments
       │ accepted reusable lesson
       ▼
ai_setup pull request and release
       │ read-only retrieval
       ▼
Hindsight and developer machines
```

## Ownership

| Content | Authority | Access |
| --- | --- | --- |
| Current application architecture, runbooks and release evidence | Application repository | Project team |
| Raw Claude/Codex prompts, responses and tool calls | Entire private checkpoint repository | Same or narrower than application source |
| Draft findings and cross-team discussion | Agent Wiki proposal folders | Individual/team ACLs |
| Approved reusable skills, rules and lessons | `ai_setup` Git review and release | Intended library audience |
| Semantic copy of released lessons | Hindsight | Read-only for normal developer clients |

Never upload raw Entire checkpoints to Agent Wiki, Hindsight or the public
`ai_setup` repository. Entire's redaction is a useful safeguard, not proof that a
transcript contains no credentials, customer data, screenshots or private source.

## One central Agent Wiki server

Every developer connects to one server. Do not install a separate Wiki on each
workstation. The `hub` component installs `ai-agent-wiki-server`, a small deployment
wrapper that fetches the exact upstream `onyx-dot-app/agent-wiki` commit recorded in
`manifest.json`. Application images are built from that checkout; they are not
cached in this repository.

The central host needs Git, Docker and Docker Compose v2. For a loopback pilot:

```bash
ai-agent-wiki-server install
ai-agent-wiki-server status
```

For developers on other machines, place a same-host HTTPS reverse proxy and DNS name
in front of the server first, then deploy with a signup allowlist:

```bash
ai-agent-wiki-server install \
  --public-url https://agent-wiki.example.com \
  --allowed-emails '*@example.com'
```

The helper refuses remotely reachable HTTP and refuses an HTTPS deployment without
an email allowlist. It generates a private secret in the upstream checkout's `.env`,
turns off the upstream development mode, enables secure cookies for HTTPS, and binds
the Compose HTTP port to loopback so clients cannot bypass the reverse proxy. It then
builds the provider's pinned Compose stack, starts it and checks the public URL. It
does not install Docker, configure DNS/TLS, open a firewall, create users or replace
an existing `.env`. Back up both the Wiki Git data and PostgreSQL; permissions,
comments and service state are not recoverable from the Markdown Git repository alone.

The first registered account becomes administrator. The administrator should:

1. Create `/proposals/<developer>/<project>/` folders.
2. Give each developer write access only to their own proposal folder.
3. Make approved/reference folders read-only to ordinary agent credentials.
4. Disable automatic application of Wiki organization/update proposals.
5. Require individual, revocable MCP keys. Never distribute an administrator key.

Agent Wiki can use Ollama or a hosted provider for its own updater and natural-language
features. That model is optional for this architecture. Leave those features disabled;
Claude and Codex can search, read, write and comment through MCP using their existing
local authentication.

## Connect a macOS or Ubuntu/Debian developer

Create an individual MCP key in Agent Wiki, then store it outside Git. The team
endpoint is already configured in `manifest.json`; use `AGENT_WIKI_MCP_URL` only to
override it for another deployment:

```bash
mkdir -p ~/.config/ai-setup
chmod 700 ~/.config/ai-setup
printf 'AGENT_WIKI_TOKEN=%s\n' 'PASTE_INDIVIDUAL_KEY_HERE' >> ~/.config/ai-setup/secrets.env
chmod 600 ~/.config/ai-setup/secrets.env
bash install.sh install
```

The default one-click profile detects either `AGENT_WIKI_TOKEN` or
`AGENT_WIKI_API_KEY`, registers the MCP without `codex mcp add`, and performs an
authenticated MCP initialization. Codex reads the token from the private file at
request time. Claude Code's HTTP MCP
configuration references `AGENT_WIKI_TOKEN`; launch Claude from an environment that
defines it. Restart both clients after registration.

## Connect a native Windows x64 developer

Use an individual key and PowerShell. The existing native Windows installer does not
require WSL:

```powershell
$secretDirectory = Join-Path $HOME '.config\ai-setup'
New-Item -ItemType Directory -Path $secretDirectory -Force | Out-Null
Set-Content -Path (Join-Path $secretDirectory 'secrets.env') -Encoding UTF8 -Value 'AGENT_WIKI_TOKEN=PASTE_INDIVIDUAL_KEY_HERE'
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Restrict `secrets.env` to the current user, SYSTEM and Administrators. Set
`AGENT_WIKI_TOKEN` in the environment that launches Claude Code. Start a new terminal
after installation so the managed user PATH is active.

The Agent Wiki administrator email and password are server-management credentials;
they are not MCP client credentials and are never copied to developer machines.
Each developer or machine uses an individual revocable API key.

## Entire on developer machines

Entire is installed by the default `all` profile on macOS, Ubuntu/Debian and native
Windows x64. Installation does **not** enable capture in any repository.

For each approved private project, create a dedicated private checkpoint repository,
then opt in from the source checkout:

```bash
entire enable --checkpoint-remote github:YOUR_ORG/PROJECT-entire-checkpoints
entire status
```

Choose only Claude Code and Codex when prompted. Keep one checkpoint repository per
source repository, with the same or narrower membership. Before rollout, verify the
project's retention policy, provider redaction rules and screenshot restrictions.
Use `entire disable --uninstall` to remove the repository hooks.

## Project publication checkpoint

MCP registration does not ingest repositories or past conversations. At a meaningful
checkpoint—a durable decision, correction, failed approach, PoC result, migration,
release finding or adopted solution—the agent must:

1. update the owning application's canonical docs and evidence;
2. search Agent Wiki for the project's existing page set;
3. create or refine pages under the current user's project proposal area—use one
   page for a small project, or a short hub plus focused domain pages when the
   project has many repositories or durable concerns;
4. record the source repository, path, revision, date, evidence status and limits;
5. preserve superseded reasoning and link its replacement; and
6. promote only reviewed, generic lessons into `ai_setup` Git and Hindsight.

Do not publish routine chat, raw transcripts, credentials, customer data, private
source or unreviewed runtime output. If the MCP is unavailable or write access is
missing, report the publication as pending; do not claim synchronization.

Keep domain pages bounded by stable concerns such as architecture and ownership,
data and money, CI/CD and releases, quality and acceptance, product decisions,
operations, and native delivery. The hub should route readers and agents; it should
not duplicate every detail from its children or the owning repositories.

## Contribution workflow

A reusable proposal must contain:

- source repository, path and commit;
- date and developer/agent attribution;
- what was tried and what failed;
- the replacement and verification evidence;
- privacy classification and reuse limits.

Review comments and corrections in Agent Wiki. Once accepted, sanitize the proposal
and submit an `ai_setup` pull request. Merge and release remain the approval boundary.
Refresh Hindsight only from that approved revision. Deleting a proposal or checkpoint
does not automatically delete copies from Git clones, backups or derived indexes.

## Verification

On every developer machine:

```bash
entire --version
entire status                 # inside an opted-in repository
ai-setup status
```

In Claude and Codex, inspect MCP status, search Agent Wiki for a synthetic proposal,
read it, add a comment in the caller's own proposal folder and verify the Git-backed
page history. Do not use private project content for the first connectivity test.

The automated installer verifies the Entire binary, local MCP configuration and an
authenticated Agent Wiki MCP initialization. It cannot prove ACL enforcement,
cross-machine visibility, backups or checkpoint retention without a real server,
individual accounts and a private test repository.
