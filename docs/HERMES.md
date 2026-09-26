# Hermes Agent integration

Hermes is installed for the current OS user, across projects. Its maintained
adapter is [`custom/skills/hermes-workflows`](../custom/skills/hermes-workflows/SKILL.md).
Codex discovers the shared skill; Claude gets a link/junction. The `hermes`
component also appends a small managed discovery block to both clients' global
instructions. Other agents can read the same skill if they support local skills
and command execution. Application workers are not automatically integrated.

## Install

From this checkout, after the normal prerequisites in [README](../README.md#install):

```bash
bash install.sh
```

Native Windows, without WSL:

```powershell
.\install.ps1
```

Those default commands install the full environment, including Hermes. For
selective repair of Hermes on an existing setup:

```bash
bash install.sh install --only hermes
```

```powershell
.\install.ps1 -Only hermes
```

Hermes is part of the default setup. Selecting only `hermes` installs its
adapter as well; selecting only `custom` installs guidance without the runtime.
Use the current Windows user profile: the upstream installer registers that
user's PATH, so alternate `-HomeDirectory` values are rejected for this component.
Source installation supports Linux and Apple Silicon macOS; upstream does not
support Intel macOS. Native Windows support is implemented but needs a Windows
runner for actual execution verification.

## Source and data ownership

- Provider: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent).
- Exact source revision: `manifest.json`, source ID `hermes-agent`.
- Downloaded checkout: `~/.agents/skills/.sources/hermes-agent`.
- macOS/Linux data: `~/.hermes`; command: `~/.local/bin/hermes`.
- Windows data: `%LOCALAPPDATA%\hermes`; command directory: its `bin` folder.
- Shared skills: `~/.agents/skills`, added to `skills.external_dirs` in Hermes config.

The installer fetches the immutable commit, then runs the provider's prerequisite,
runtime, dependency, config and product stages. It deliberately omits the provider
repository-update stage, which otherwise follows a mutable branch. Source, Python,
Node, dependencies and bundled skills remain downloaded artifacts outside this repo.
The provider owns its dependency locks and launcher generation.

Browser tools are skipped using the provider's supported switch. To enable them
later, run `hermes pm install agent-browser`. The upstream CLI installation builds
its TUI and web assets but does not launch a server. This integration does not
install/start a gateway, create schedules, connect messaging or configure a paid
provider. See the [upstream installation contract](https://hermes-agent.nousresearch.com/docs/getting-started/installation).

Existing settings and external skill directories are preserved. Config is backed
up before adding the shared directory; YAML formatting/comments may be normalized.
No credentials or project conversations are copied. Hermes-created skills default
to its profile-local directory; an existing explicit `skills.create_dir` is preserved.
External directories are writable by Hermes: this is an instruction boundary, not
filesystem enforcement. Review learned material before promoting it into this repo.

Hermes profiles may have different configuration, credentials and skill paths.
The installer configures the default data home; check the chosen profile before
assuming it sees the same skills. Claude/Codex role files and MCP registrations
are not imported automatically into Hermes.

## Start and verify

Open a new terminal/client, then:

```text
hermes --help
hermes doctor
hermes model
```

`hermes model` is the interactive provider login/selection step. Do not infer model
access from a successful install. A real model task is a separate verification
step after the user configures access. The installer runs CLI help and verifies
the pin, origin, unmodified provider source, shared skill config and managed files.

Rerun the same installation command after a failed download/build. It preserves
unmanaged launchers, local source changes and existing custom skill edits. Review
collisions before relocating a previous installation. Avoid `hermes update` on
this managed checkout: deliberate upgrades require updating the manifest pin and
preserving/moving the old source before installation. Keep the Hermes data home,
sessions and credentials intact. Run `setup.py verify` after any planned update.

## Verification scope

Regression tests cover config preservation, malformed config, native Windows
command construction, alternate-home rejection, actual installer retry/rerun
against a local provider fixture, shared skill installation and source-drift refusal.
Run with the setup virtual environment:

```bash
python -m unittest discover -s tests -p test_hermes.py -v
```

These offline tests do not establish Windows runtime support, model access,
scheduled delivery or messaging connectivity. Those require their actual platform
and authorized provider configuration.

On 2026-09-26, the real provider installation and repeated installation passed on
Apple Silicon macOS. CLI help, installed-state verification and actual shared-skill
discovery passed, including the local `hermes-workflows` adapter. Hermes's own
bundled `hermes-agent` skill is separate, so the adapter has a distinct name.
Doctor confirmed the runtime and reported optional tool/authentication gaps. It
also reported one high vulnerability in the upstream browser dependency lockfile;
the browser tool itself was not installed. No local patch was applied to provider
dependencies. Live model calls, schedules and messaging were not exercised.

The [Hermes workflow](../.github/workflows/hermes.yml) runs provider installation,
repeat installation and shared-skill discovery on Ubuntu, macOS and native Windows
after push (or manual dispatch). Those runner results are pending; local Windows
checks validate command construction and guards only.
