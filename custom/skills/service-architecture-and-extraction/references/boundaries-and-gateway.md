# Service boundaries and gateway extraction

## Select boundaries with evidence

Assess change ownership, transaction coupling, secrets/data access, scaling characteristics, deployment cadence and operational cost. Code size alone is insufficient. Measure an alleged bottleneck: latency, throughput, CPU/memory, connection budgets, database locks and critical paths. More processes can add latency, failure modes and database pressure.

Name the distinction being introduced:

- Module: logical responsibility inside one application.
- Repository/package: source and version ownership.
- Service: runtime authority with a defined interface and operational lifecycle.
- Infrastructure boundary: process user, network, VM/container, database role/schema or physical database.

A repo split can improve parallel context without requiring a physical database per repo. A shared primary remains a shared failure/operational boundary even with least-privilege roles. Record cross-domain reads, onboarding transactions, compatibility proxies and other transitional coupling explicitly.

For each component, document owner, responsibilities and exclusions; interfaces and consumers; authoritative writes and permitted reads; secrets/configuration; durable/ephemeral resources; tests/observability; deployment/rollback needs. Do not infer independence from a name or directory.

## Financial and personal-data boundaries

Separate identity/session authority from business membership and authorization. An authenticated actor is not automatically entitled to every tenant, location, field or action.

Distinguish provider credential/crypto/transport responsibility from collection records, invoices, subscriptions/entitlements, order fulfillment, refunds and settlement. Different business domains may call a provider wrapper with distinct scoped credentials. A common provider does not make their ledgers interchangeable.

Inventory PII across profiles, membership, party records, immutable documents, logs, events, backups and exports. Extracting a party directory does not automatically relocate every personal field or establish compliance. Keep minimization and lifecycle decisions explicit; legal/financial retention requirements need their own verified policy.

## Gateway versus operations

The gateway owns runtime traffic behavior: route selection/composition, trusted forwarding, upstream connection behavior and any intentionally centralized edge policies. Ops owns installation, release orchestration, process definitions, configuration delivery, deployment evidence and recovery. Host TLS/DNS/proxy infrastructure may have another owner. A dedicated gateway repo is optional; select it when ownership or release needs justify it.

The gateway need not own service business logic or all API contracts. Service authorization remains enforced at the protected operation even when the edge performs authentication. Inventory direct service, worker, server-rendered and webhook access paths that can bypass browser routing.

For a forwarding gateway, preserve and test the actual protocol contract:

- Route precedence and aliases; malformed/encoded paths; private routes and assets; host/custom-domain routing when supported. Interpret paths consistently across layers to avoid route-confusion bypasses.
- Remove hop-by-hop headers, including headers named by `Connection`. Do not forward user-supplied identity/network hints as trusted facts.
- Trust forwarded client IP/protocol/host only according to the actual proxy chain and known peer configuration. Do not universally assume either the first or last forwarded IP is trustworthy. Verify direct-origin and multi-proxy behavior, and use maintained proxy support where suitable.
- Preserve required cookies, raw webhook bodies, streaming, query strings, redirects and cancellation semantics. Explicitly identify WebSocket/SSE support rather than assuming it.
- Apply appropriate request/response limits, timeout budgets and cleanup on abort/error; do not buffer unbounded bodies. Login/input limits can be lost when moving a route adapter, so carry them into the new authority.
- Keep upstream failures actionable and generic to clients, while logging safe diagnostic/request context. Rate limiting needs correct client identity and multi-instance behavior.

Bind services to the intended interface and authenticate service-to-service calls according to the deployment threat model. Loopback is an exposure control, not authorization against other local processes. Verify listeners/firewall from the relevant environment rather than assuming a configuration file is active.

## Extraction sequence

1. Capture current public URLs, actor flows, API/SDK compatibility, provider settings, schema/data ownership and critical negative tests.
2. Choose one bounded capability. Define transition adapters and shared-resource privileges; retain transaction authority unless a replacement recovery protocol is designed.
3. Move source with explicit ownership; preserve contract artifacts and route behavior. Verify independent install/build without hidden sibling imports or parent assets. Inspect packaging for personal config/secrets.
4. Prepare scoped environment/process/database access. Migrate additively and verify the actual schema and privileges before changing traffic. Do not enable disabled providers as a side effect.
5. Deploy compatible consumers/producers and routing in a safe order. Drain relevant workers/writers; exercise the public workflow and negative paths against the intended revisions.
6. Record compatibility and observed deployment evidence. Test rollback against the current schema. Remove adapters or legacy storage only with a separate, evidenced retirement decision.

A UI-only compatible change may deploy independently; a breaking contract or data migration may require staged coordination. Never tell users that every repo can always be released independently merely because it has its own deployment command.
