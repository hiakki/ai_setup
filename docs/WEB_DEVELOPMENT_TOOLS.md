# Web development tools

These integrations support business apps, video-editor interfaces and other web projects.
They provide documentation, security testing and UI context; they do not supply video
encoding or editing engines. Installer selections are documented in the root README.

## Context7 — default `context7` component

Registers `https://mcp.context7.com/mcp` in `~/.codex/config.toml` and `~/.claude.json`.
No local server or npm package is needed. The hosted service is provider-managed and
cannot be pinned like a Git checkout. Anonymous access has a provider rate limit.

Managed global instructions direct agents to resolve a library with `resolve-library-id`,
then retrieve documentation with `query-docs`. Start a new client session to discover it.
Send minimal technical queries, not private source or credentials.

Existing stdio, HTTP, OAuth, header, timeout and disablement settings are preserved,
including operator changes after installation. Invalid entries fail explicitly. Existing
credentials are not copied into installer state. Verification checks registration,
not remote service availability.

For higher limits, use the [provider's authentication instructions](https://context7.com/docs/resources/all-clients)
with client-supported environment references or OAuth. Do not commit keys. Account
setup is optional and is not performed by installation.

## UI skills — default `skills` component

Two skills come from the original [ibelick/ui-skills](https://github.com/ibelick/ui-skills)
repository at the manifest commit, including its license:

- `create-design-md`: document a product's design system from repository or rendered-site
  evidence. The skill uses `@google/design.md` lint/export when invoked; that on-demand
  dependency is not installed by this setup. Website mode needs a browser.
- `fixing-metadata`: audit titles, canonical URLs, social cards, robots and structured data.

They are shared through `~/.agents/skills` and Claude's skill directory. Existing design
suites remain available; the overlapping UI Skills registry is not bulk-installed.

## Strix — optional `strix` component

Downloads the official [Strix](https://github.com/usestrix/strix) v1.6.2 release, verifies
the manifest's platform SHA256, checks the CLI, and installs `~/.local/bin/strix`
(`strix.exe` on Windows). Nine upstream skills are fetched at the corresponding release
commit. Installing the suite preserves its cross-skill references.

Both clients receive discovery guidance. Existing security roles can use
`penetration-testing-with-strix` and `application-security-testing`; no duplicate role
is needed. `strix --version` and `strix --help` verify installation, not scan readiness.

The CLI has native macOS/Linux x64 and ARM64, and Windows x64 releases. Windows CLI
installation needs no WSL. **Local scans** need a Docker Linux-container backend and
a configured model. A Windows Docker backend may use WSL2, Hyper-V or a remote Linux
host; this installer does not provision it. See the [upstream quickstart](https://docs.strix.ai/quickstart)
for model authentication. Managed cloud is a separate account and data-transfer choice.

Before scanning, establish the authorized target, scope and budget. Installation does
not start Docker, pull sandbox images, upload source, schedule scans or authorize spending.
Do not fall back to cloud automatically. Remote LLM use may also send code off-machine.
Use a disposable authorized checkout: upstream documents that local targets are writable.

## SkillUI — optional `skillui` component

Installs [amaancoderx/npxskillui](https://github.com/amaancoderx/npxskillui)'s `skillui@1.3.4`
from npm into a separate managed prefix, exposing a user-level CLI. It reuses Node 18+
and npm from `runtime` or PATH. Existing and locally edited installations are preserved;
failed staging can be retried.

Both clients receive usage guidance. In the relevant project, with `.agents/` ignored:

```sh
skillui --help
skillui --dir . --out ./.agents/skillui --name my-app --format design-md
```

The same commands work in PowerShell. Keep generated context in its project and review
extracted values before treating them as design decisions. Default directory extraction
needs no API key or browser. Browser/ultra workflows require separate Playwright setup
and are not automatically enabled. Use `create-design-md` for a small evidence-led
document and SkillUI when automated extraction is useful.

## Provenance and verification

Third-party skills, binaries and dependency trees are fetched at install time, not
vendored here. Git commits, Strix hashes and SkillUI's top-level npm version are pinned
in `manifest.json`; transitive npm dependencies remain resolver-dependent. Only adapters
and discovery guidance live here. See [verification evidence](VERIFICATION.md).
