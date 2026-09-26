---
name: hermes-workflows
description: Use the locally installed Hermes Agent for persistent research, reusable task memory, or explicitly requested scheduled and messaging workflows. Applies when a task benefits from Hermes or the user names it.
---

# Hermes Agent

Hermes is a separate agent runtime. Discover the installed command with `hermes --help`.
On macOS/Linux the fallback is `~/.local/bin/hermes`; on Windows use
`%LOCALAPPDATA%\hermes\bin\hermes.exe` (or `hermes.cmd`, depending on the provider's
launcher). Respect an explicitly selected Hermes profile.

- Inspect `hermes chat --help` before constructing a noninteractive request. Give it
  a bounded task, authorized working directory, expected output and stopping condition.
  Delegating to Hermes is agent delegation: obey the host's delegation rules.
- Run `hermes doctor` to diagnose availability. If provider access is absent, ask the
  user to run `hermes model`; never scrape other clients' credentials or claim a live
  model task passed from CLI installation alone.
- Review returned evidence and artifacts in the originating task. Hermes memory and
  sessions are separate from the caller's conversation; pass necessary context explicitly.
- Existing shared skills are configured through `skills.external_dirs` pointing at
  `~/.agents/skills`. Client-specific tool names and agent roles are not automatically
  portable; confirm required tools before using a skill in Hermes.
- Keep newly learned skills in Hermes's profile-local `skills/` directory. External
  skill folders are writable, not sandboxed: do not ask Hermes to patch or delete the
  shared collection. Review useful lessons, remove secrets/project-specific context,
  then promote them into `ai_setup/custom/skills` and reinstall through its installer.
- Read `hermes cron --help` or `hermes gateway --help` only when those workflows are
  requested. Installing Hermes does not authorize recurring model costs, messages,
  publishing, production writes, service starts or an unattended gateway.

The `ai_setup` default `hermes` component downloads a pinned upstream source and
uses its installer for dependencies. Normal `install.sh` / `install.ps1` runs include it.
For selective install/repair from an `ai_setup` checkout:
`bash install.sh install --only hermes` on macOS/Linux, or
`.\install.ps1 -Only hermes` on native Windows. The standalone skill does not install
the runtime. Avoid `hermes update` on this managed installation: update the repository's
pin deliberately and preserve the old source before reinstalling.

Provider references: [Hermes](https://github.com/NousResearch/hermes-agent),
[skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills),
[scheduled tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron).
