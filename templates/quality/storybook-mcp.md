# App-owned Storybook MCP activation

Use only in an application authorized for Storybook changes. Check its installed
Storybook/framework versions first. This recipe targets 10.6.2; do not force an
upgrade into an incompatible application. The upstream AI interface is preview.

For an already compatible app, use its package manager to pin
`@storybook/addon-mcp@10.6.2` as a dev dependency and add
`'@storybook/addon-mcp'` to the existing `.storybook/main.ts` `addons` array.
Preserve all existing configuration. Where the framework supports it, merge:

```ts
features: { componentsManifest: true }
```

Start through the app's documented Storybook command with owner authorization.
Use its actual loopback port, then inspect `/mcp` and the component manifest.
Register a uniquely named HTTP server for that project in Claude/Codex using
their installed CLI help. Keep personal registrations ignored; do not replace
other MCP settings or register a generic port globally. Only after tools/list
and `docs-list` return the app's real components is the connection verified.
Use `docs-show` before selecting component properties, and the available story
instructions/test tools when supported. Do not invent component APIs or assume
all frameworks provide the same tools. A healthy endpoint alone is insufficient.

Source: https://storybook.js.org/docs/ai
