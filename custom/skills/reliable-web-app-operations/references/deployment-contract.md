# Deployment Contract

## Environment

Treat the example environment file as a versioned key contract, not a production configuration.

- Parse keys structurally; do not source the file merely to discover names.
- Append only missing keys to an existing environment file.
- Never overwrite an existing value during synchronization.
- Mark newly appended values for operator review.
- Validate booleans, URLs, ports, prefixes, and provider credential shapes before build or restart.
- Keep server-only and public variables distinct. Do not add duplicate names unless the framework genuinely requires both scopes.

## Command Boundaries

| Command | May install prerequisites | May build app | May restart app | May mutate data |
| --- | --- | --- | --- | --- |
| prerequisites/setup | Yes | No | No | No |
| deploy | Only missing app prerequisites | Yes | Yes | Only explicit migrations |
| monitoring setup | Monitoring prerequisites only | No | No | No |
| health/status | No | No | No | No |
| seed/reset | No | As needed | Explicit only | Yes, with environment guard |
| backup/restore | Storage prerequisites only | No | Explicit only | Yes, audited |

Do not hide a deployment inside monitoring, SSL, proxy, or backup setup. Print the plan before mutation and make dry-run behavior available for risky scripts.

## Compatibility

- Detect operating system and package-manager capabilities instead of assuming package names.
- Prefer `docker compose`; support legacy `docker-compose` only as a detected fallback.
- Verify runtime versions before invoking runtime-dependent helpers.
- Detect who owns ports 80/443 before trying to start another reverse proxy.
- Validate configuration before reload and preserve a known-good backup.

## Release Evidence

Keep these claims separate:

1. Source validation: lint, type check, unit tests, config parsing.
2. Built artifact: production build succeeds.
3. Local runtime: changed flow succeeds in a fresh process.
4. Deployment: target process runs the intended release and environment.
5. Public path: DNS, TLS, proxy, and application flow work through the customer URL.
6. Provider/live completion: the actual external outcome is confirmed.

A lower level never proves a higher one.

