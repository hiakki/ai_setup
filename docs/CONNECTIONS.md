# Private connections

The original machine has Codex MCP registrations named `hyperdx-prd`, `hyperdx-stg`, `servinoza-diagnostics`, and `stripe`, in addition to the portable Codebase Memory/Graft/Playwright/Figma set. These private registrations are not hard-coded into a public setup repository.

Provision each integration using the intended account, endpoint, and its current provider-supported transport. Do not copy an entire `.claude.json`, Codex config, OAuth cache, browser profile or keychain to another machine. Configuration presence is not a successful provider request.

For an HTTP endpoint, the client commands are:

```bash
codex mcp add SERVICE_NAME --url "$SERVICE_MCP_URL"
claude mcp add --scope user --transport http SERVICE_NAME "$SERVICE_MCP_URL"
```

Use the provider's OAuth flow or a client-supported token environment reference. Do not place the token in a command argument, tracked JSON, or this repository. Some private services only support one client or a custom gateway; verify that actual service before adding a second registration.

Laya can use `LAYA_ENDPOINT` and `LAYA_API_TOKEN` directly. `TYPESAFE_API_KEY` and `SCRAPECREATORS_API_KEY` enable their respective skill workflows. Blog image/audio/Google integrations need their own dependencies and accounts. Installation makes guidance available without forcing paid or authenticated calls into startup.
