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

When the user requests separate documentation or database-operations ownership,
evaluate that boundary directly. Being technically possible inside an ops repo is
not a reason to dismiss it, and a previously recommended repository count is not
an invariant. A dedicated repository can own documentation publication or runnable
database tooling without becoming an HTTP service. Keep domain contracts and
migrations with their authorities; specify who imports, validates and publishes
the former, and who builds, schedules and executes the latter. Record one owner
for each environment setting and runtime credential. Verify the resulting workflow,
not just a renamed repository table; label proposed jobs and untested recovery
separately from implemented automation.

## Frontend ownership and shared-package release boundaries

Choose source access, package dependencies and runtime releases separately. A
frontend monorepo can contain independently deployed apps; a separate design-system
repo can own generic components/tokens when maintainer permissions justify it.
Ordinary screen engineers can then use one clone, while foundation maintainers
need a second. State that tradeoff rather than promising all UI edits in one repo.
Keep domain-specific components with their app and authoritative permissions,
stock, tax and payment decisions with backend services.

Direct workspace links consume shared source on the consumer's next build. A
package version field alone does not isolate that source. For explicit upgrades,
publish immutable artifacts, pin exact versions per consumer, commit lockfiles
and prohibit production sibling-directory links and mutable-branch shortcuts. A monorepo can
also use this publication discipline; repo separation alone is not the safeguard.
Version token/style dependencies too and prevent global asset updates from
bypassing package pins. Verify registry capabilities and read/publish permissions.

CODEOWNERS with required review rules provides governance, not directory-level
read/write isolation. Verify effective rules, account-plan support and bypasses
before claiming enforcement. Run affected-consumer checks against candidate
packages, but promote apps only through their own approved dependency upgrade and
release. Broad tests must not imply broad deployments. Root lockfiles/tooling can
affect multiple apps even with exact package pins; record that residual coupling.

Acceptance: fresh consumer-only clone installs without sibling source; two apps
resolve different package versions; publishing leaves existing consumers
unchanged; one upgrade deploys only that app; previous image/artifact rollback
works. Track security-update deadlines so version isolation does not retain
vulnerable dependencies indefinitely. CI stays with its existing platform owner;
do not introduce service-owned pipeline copies to enable package publishing.

Repo layout does not establish throughput. Evaluate workload mix, cache hit rate,
fanout, transaction contention and per-replica connection budgets before scaling
claims. Team/access boundaries may justify future source splits independently of
requests per minute. See the dated frontend corrections in the central extraction
case for provenance; target-specific acceptance tests remain required.

### Developer handoff is a runtime boundary

A source-only install/typecheck is not an end-to-end handoff. For multi-zone UIs,
provide one local browser origin routing pages, server-rendered reads, browser
APIs, assets and explicitly allowed HMR WebSockets. Keep routing with its platform
owner and distribute a pinned artifact, rather than requiring every frontend
engineer to clone backend/gateway source. Verify real registration, sign-in/out,
mutation/reload, denied access and an actual hot-reload edit in a clean consumer
checkout. A production HTTP proxy may not support development WebSockets.

For routine frontend integration, a dedicated synthetic shared backend can reduce
laptop setup. Give individual revocable environment access and ordinary scoped
app accounts, never internal service or database credentials. Check environment
identity and readiness before starting the UI or sending provisioning mutations.
Validate local Host/Origin before proxy rewriting. Preserve Secure/HttpOnly/
SameSite; test the actual browser and API client's cookie handling. Ports do not
isolate cookies: use distinct sandbox namespaces and filter unrelated cookies in
both directions, especially when a development API shares an HTTPS hostname.

Backend contributors should run their own service with pinned dependency images
and fresh isolated synthetic databases, rather than attach arbitrary source to
the shared environment using broad internal tokens. Check for orphan volumes
before claiming initialization is fresh. Keep source listeners loopback and test
Docker-host bridging on the actual supported OS. A Docker administrator can read
local synthetic credentials; repository boundaries do not prevent that.

A schema-only disposable bootstrap is not evidence that production migrations
ran. Publish its provenance and compatible image set, omit customer data/history,
and leave production migration checks intact. Distribute a versioned tooling
bundle so onboarding does not require infrastructure repository access. Keep
provider side effects disabled and explicit; component stories, API reads and
simulated payments establish different levels of evidence.

When relocating Next standalone apps, inspect the generated server, asset and
writable-cache paths. A nested server can move its cache outside an existing
container mount; prove write-through using the final read-only runtime contract,
not only a development build. Keep rollback artifacts compatible with the old
source URL while binding new releases to their actual source owner and app path.

Versioned release assets may be vendored with integrity receipts when a separate
package registry adds unnecessary credentials. A vendored artifact is not a live
sibling-source link: verify packed identity, exact consumer pin, lockfile integrity
and publication provenance. Candidate packing may differ across npm versions or
hosts. In a disposable compatibility checkout, re-resolve only the candidate's
lock entry; never overwrite an immutable release, disable integrity checks or
rewrite production locks merely to accept different bytes at the same version.

Pinned deployment tooling must not be compared only with a moving branch tip.
Fetch the approved branch freshly, verify the pinned commit remains reachable,
and archive that exact commit without moving the checkout. Reject unpublished
commits, rewritten-away history and failed fetches; test all four cases. When
source ownership changes, review image validators, cleanup allowlists and every
deployment adapter as well as build labels. Keep runtime identities independent.

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
