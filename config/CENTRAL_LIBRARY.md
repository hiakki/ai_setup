# Central authoring and search policy

Reusable AI skills, agent definitions and generic AI learning/documentation have
one canonical home in ai_setup. Applications consume that global installation.
Application architecture, business decisions, design docs, runbooks, plans and
release/test evidence stay in the application's own repository. This ownership
split, clarified on 27 September 2026, supersedes the earlier blanket requirement
to author all documentation centrally. Promote only project-neutral AI lessons.

ai_setup exists to improve the shared AI setup across projects: skills, agents,
rules, workflows, AI learning discussions and reviewed self-learning. It is not a
store for individual apps' discussions, decisions or conversation transcripts.
Documentation for ai_setup's own installers, integrations and operation stays here.

Curated, sanitized project case studies are shared AI learning when they explain
reusable decisions, failures, tradeoffs and evidence. Keep them in
`docs/case-studies/<origin>-<topic>.md`; retain full/current project docs with their
owner. Include search aliases, source project/path/revision, review date,
implemented versus proposed status, verification limits and links to the relevant
skills. Do not publish raw discussions, transcripts, secrets or private product
details. A source project name is a discovery key, not permission to mirror it.

## Current app state and accumulated experience

Applications maintain their current architecture, cron/background-job ownership
and schedules, CI/CD, operations and release evidence in their own docs. Update
the relevant current-state section when the task changes it; keep original ADRs
and dated evidence with the app. Mark proposals and superseded instructions so
readers can identify the active approach.

The central `docs/PROJECT_CATALOG.md` holds portable owner-source pointers and
review baselines, not duplicate architectures. Find it with
`ai-setup search "project catalog"`. Before adopting an existing implementation,
read its current authorized docs/source and record freshness and target fit.
Central `--refresh` does not refresh referenced app repositories.

Before closing a significant correction, failure, migration, switch or release
that teaches a reusable lesson, follow `docs/LEARNING_WORKFLOW.md` (search
`"learning workflow"`). Preserve approach tried, result, reason for switching,
replacement/status, verification limits, provenance and reuse conditions in the
existing case. Retain failed/superseded decisions, not just successful outcomes.
Improve the relevant existing skill when a general rule is missing. This is
agent workflow guidance, not an automatic transcript collector or publishing job.

## Search before authoring

```sh
ai-setup search "release deployment"
ai-setup library
```

Before proposing substantial architecture, service extraction, CI/CD, security or
QA work, search by topic and any named reference project, read relevant cases and
their linked skills, and explain which decisions you adopt, adapt or reject for
the target. Do this before writing recommendations, not only when authoring skills.
Find the case index with `ai-setup search "engineering playbook"`.
Search uses literal words, not semantic retrieval; try `cicd` and `CI/CD`, or
`microservices` and `service extraction`, when a query misses relevant material.
It does not read arbitrary sibling projects or previous conversations.

Read matching entries before creating shared AI material. For application work,
also read the project's own source-of-truth docs. Search includes bound central
checkouts, the installed documentation bundle, global skills and Claude/Codex roles.
Results include origin, path and line number; identical reference copies are deduplicated.
This is local text search, not semantic retrieval or a search of every remote file.
It skips links, binary files, environment files, dependency/build folders and files over
2 MiB. Zero results are not proof that no relevant remote content exists.

For current remote content, run `ai-setup search "TOPIC" --refresh`. This invokes the
existing trusted-repository update workflow and fails if the update fails. Otherwise
search explicitly reports that remote freshness was not checked. No scheduler or
background synchronization is installed. Unpublished changes cannot be fetched.

## Reuse and improve shared learning

1. Before a task, search for relevant shared guidance and read the applicable entry;
   read application facts from the application's own docs.
2. When a user correction, recurring failure or verified solution yields a reusable
   lesson, update its existing central skill, rule or learning entry within the
   authorized scope. Do not require the user to repeat it in each project.
3. Record the general trigger, recommended action, verification and limitations.
   Keep AI learning discussions here only when they concern reusable improvements;
   label untested ideas as proposals and retain evidence for validated guidance.
4. Keep project-specific decisions and evidence in the owning repository. Extract
   only the generic lesson; do not copy transcripts, customer data or secrets.
5. Check for duplicates or conflicting advice and apply the relevant lesson on
   future tasks. Publish and update other installations only when authorized.

Self-learning here means maintaining reusable knowledge, not retraining models or
guaranteeing that every agent will recall every conversation. Installed guidance
must still be discovered and followed; no automatic background sync is implied.

## Author shared AI material at the central source

The `hub` installer binds its Git checkout when no authoring checkout has been chosen.
Downloaded release caches are never bound as authoring locations. To choose another:

```sh
ai-setup library --checkout /path/to/ai_setup
```

| Material | Central authoring path |
| --- | --- |
| Custom skill and all supporting files | `custom/skills/<name>/` |
| Custom agent role | `custom/agents/<name>.md` |
| Original-provider skills/roles | Provider source; selections and pins in `manifest.json` |
| Generic AI learning, reusable discussions and shared documentation | Existing canonical entry, or `docs/shared/<topic>.md` for a new topic |
| Curated, sanitized project case studies | `docs/case-studies/<origin>-<topic>.md`, linked from the engineering playbook and relevant skills |
| Current app documentation discovery | `docs/PROJECT_CATALOG.md`: owner-relative pointers, aliases, review baselines and gaps; details remain with the app |
| Application architecture, decisions, design, runbooks and release evidence | The application's own repository and existing docs conventions |
| Private reusable AI skills, roles or learning | A separately authorized private library, never the public ai_setup repository |

Existing top-level shared docs remain canonical; update them in place instead of making
duplicates. Custom agents use YAML `name` and `description` frontmatter plus Markdown
instructions. The `agents` component creates both Claude and Codex adapters.

Private reusable AI material must never be added to the public library. Bind an authorized private
repository with `ai-setup library --checkout /path/to/private-library --private`.
`--private` is an operator declaration, not a verification of remote access controls.
Without that destination, stop before authoring private shared AI material and ask for it. Application
docs need no central binding; maintain them in their owning repository. Never
store credentials in either library. Search can read a bound private checkout on that
machine; this implementation does not automatically clone, publish, install or update it.

Do not edit installed reference copies as a competing source. Publication requires the
normal review/commit/push workflow. New shared content reaches another machine after an
approved update. Global availability does not force a client to select a skill or role.

## Commit enforcement

The `hub` component installs a per-user Git hook dispatcher on macOS, Linux and native
Windows. It forwards existing hooks, including their arguments, stdin and exit status,
and then checks staged changes before commits. Existing unchanged documents are not
blocked or migrated. Explicit `ai-setup guard remove` survives subsequent hub updates.

```sh
ai-setup guard status --project /path/to/project
ai-setup check-project --project /path/to/project
ai-setup check-project --project /path/to/project --audit
```

The gate rejects `SKILL.md` files and known client skill/agent libraries outside
bound central checkouts. Case-insensitive path matching covers those directories.
Application source such as `src/agents/worker.py` and project documentation,
including Markdown, `docs/` and `documentation/`, remain allowed. The gate cannot
infer whether ordinary prose is generic AI learning or app-specific documentation;
agents must follow the ownership rule when writing it. `--audit` also finds existing/ignored local content outside dependency
and build directories; it only reports and never deletes or moves it.

Exceptions: explicitly bound central repository roots; root README/license/notice files;
and `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `CLAUDE.local.md` routing files.
Routing files should contain pointers and necessary client instructions, referring
to global skills and the project's own docs. The gate recognizes paths, not meaning;
it cannot detect disguised skill libraries in arbitrary source files.

To restore the previous global Git hook setting, use `ai-setup guard remove`. If that
setting has been independently changed, removal preserves it and reports the conflict.

## What is and is not guaranteed

| Layer | Actual guarantee |
| --- | --- |
| Global Claude/Codex instructions | Require central search and authoring; compliance depends on the client |
| Global Git guard | Rejects matching staged changes when this hook configuration is active |
| Required CI | Can reject bypassed local changes when configured as a required branch check |
| Filesystem isolation | Not installed; unrestricted processes can still create files |

Repositories with their own `core.hooksPath` override the global dispatcher. Run the
check explicitly in their existing hooks or configure required CI; do not overwrite a
project's hook settings blindly. `--no-verify`, direct Git plumbing, config changes and
unprotected branches can bypass a client-side gate. Git documents these mechanics in
its [hook reference](https://git-scm.com/docs/githooks).

Use `ai-setup check-project --project PATH --base BASE_COMMIT` in CI to inspect changes
from an approved base to HEAD. The reusable workflow in `.github/workflows/central-library-policy.yml`
provides this gate after publication. Adopt it in each consuming repository and require
the check through its branch rules. A workflow in ai_setup alone does not protect other
repositories. No remote branch settings are changed by the installer.

Example consuming-repository workflow after publishing the implementation:

```yaml
name: Central library
on: [pull_request]
permissions:
  contents: read
jobs:
  policy:
    uses: hiakki/ai_setup/.github/workflows/central-library-policy.yml@PUBLISHED_COMMIT_SHA
    with:
      base-sha: ${{ github.event.pull_request.base.sha }}
      library-ref: PUBLISHED_COMMIT_SHA
```

Replace both placeholders with the reviewed immutable commit. Require the resulting
check in the consuming repository's branch rules. Keep the workflow and its pinned
policy revision under trusted review; otherwise an author can weaken the check itself.
