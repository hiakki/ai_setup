# Central authoring and search policy

Skills, agent definitions and authored documentation have one canonical home. Projects
consume the global installation and retain only the client configuration and routing
pointers they actually require. This policy supersedes older personal instructions to
write project-local skills, agents, context notes, plans and handoffs.

## Search before authoring

```sh
ai-setup search "release deployment"
ai-setup library
```

Read matching entries before creating another one. Search includes bound central
checkouts, the installed documentation bundle, global skills and Claude/Codex roles.
Results include origin, path and line number; identical reference copies are deduplicated.
This is local text search, not semantic retrieval or a search of every remote file.
It skips links, binary files, environment files, dependency/build folders and files over
2 MiB. Zero results are not proof that no relevant remote content exists.

For current remote content, run `ai-setup search "TOPIC" --refresh`. This invokes the
existing trusted-repository update workflow and fails if the update fails. Otherwise
search explicitly reports that remote freshness was not checked. No scheduler or
background synchronization is installed. Unpublished changes cannot be fetched.

## Author only at the central source

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
| Shared documentation | `docs/shared/<topic>.md` |
| Public project documentation | `docs/projects/<project-name>/` |
| Private project documentation | `docs/projects/<project-name>/` in a separately bound private library |

Existing top-level shared docs remain canonical; update them in place instead of making
duplicates. Custom agents use YAML `name` and `description` frontmatter plus Markdown
instructions. The `agents` component creates both Claude and Codex adapters.

Private material must never be added to the public library. Bind an authorized private
repository with `ai-setup library --checkout /path/to/private-library --private`.
`--private` is an operator declaration, not a verification of remote access controls.
Without that destination, stop before authoring private documents and ask for it. Never
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

The gate rejects changed Markdown/MDX/RST/AsciiDoc documents, files under `docs/` or
`documentation/`, `SKILL.md` files, and known client skill/agent directories. Case-insensitive
path matching covers those directories. Application source such as `src/agents/worker.py`
remains allowed. `--audit` also finds existing/ignored local content outside dependency
and build directories; it only reports and never deletes or moves it.

Exceptions: explicitly bound central repository roots; root README/license/notice files;
and `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `CLAUDE.local.md` routing files.
Routing files should contain pointers and necessary client instructions, not a second
documentation library. The gate recognizes paths, not meaning; it cannot detect disguised
documents in arbitrary source files or enforce that exception's intent.

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
