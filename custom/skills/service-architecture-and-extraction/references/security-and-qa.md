# Security and QA across service boundaries

Use a bounded threat model and risk-based test matrix. This reference captures extraction regressions and workflow lessons; it is not a full pentest methodology or a guarantee of security. For current framework/provider/security-standard specifics, consult authoritative documentation and the applicable installed specialist skill.

## Endpoint and actor matrix

Discover actual methods/handlers, generated/dynamic routes, compatibility proxies, internal APIs, webhooks and server-rendered access. A gateway prefix list does not enumerate all endpoints. Record method/path, owner, exposure, authentication, tenant/role/object/field policy and side effects.

Choose representative actors and denied cases from the application: anonymous; authenticated without membership; restricted member; owner; platform operator; second tenant; wrong location; expired/revoked session or entitlement; missing/wrong-service internal credential. Do not assume every application has all these roles.

Explicitly classify public operations, user-protected operations, privileged operations, signed webhooks and internal calls. Not every valid endpoint should require interactive login. Verify both intended access and intended denial; assert no forbidden data or mutation, not just a preferred status code. Authentication middleware passing is not proof of business authorization.

## Boundary regressions worth checking

- Limits before expensive parsing, including oversized declared bodies and streamed/chunked bodies without a trustworthy content length; preserve framework body-stream requirements and cancellation behavior.
- Invalid JSON, unsupported content types, numeric bounds, duplicate/replayed requests and ambiguous identifiers, proportional to the changed surface.
- Forged forwarding headers, route normalization mismatches, unknown hosts/origins and direct-upstream access.
- Session continuity, login throttling, cookie settings, logout/revocation and relevant CSRF/origin checks across the deployed hostname/proxy chain.
- Anonymous redirects through the real public gateway: assert the complete Location origin and follow it to the intended page. A correct redirect pathname or successful signed-in page can hide a framework URL built from a private listener hostname; correct forwarding headers alone do not establish the resulting redirect origin.
- Credential forms before hydration and when JavaScript is delayed or unavailable: native submission must not put secrets in URL query parameters. Use safe form semantics and prevent submission until the intended authenticated handler is ready; test the actual first-load browser path.
- Stored user content in actual browser rendering, uploads/remote fetches if present, and sensitive field filtering in APIs—not only hidden UI columns.
- Tenant-scoped reads/writes, resource access, service-token scope and actual database role privileges. Admin capabilities require their own policy.
- Webhook raw-body verification, wrong credential/account binding, duplicate processing and late/cancel/refund races when those flows change.

Use safe isolated fixtures for mutation and attack-like inputs. Establish authorized target, scope, cost and data-handling before active scans. Tool installation or a Docker container does not imply private source stays local; do not fall back to managed scanning or provider-backed analysis without authorization. Do not run destructive fuzzing or real financial actions against a demo/production environment by default.

Dependency audits check known advisories; assess reachability and fix risk. A zero-advisory report is not a whole-application security certification. Report concrete findings, remediation, tested scope and residual gaps. Never provide an absolute security guarantee.

## Browser QA must exercise the intended job

Use the available real-browser tool when behavior/visual interaction matters. An API test cannot prove a user can find and operate an approval button. A screenshot cannot prove the save posted the correct ledger event.

For the changed flow, test the permitted actor's actual steps and the restricted actor's behavior:

- Discovery of the action, clear terminology, role-appropriate controls, confirmation/approval state and successful persisted outcome after reload.
- Search/filter/sort/grouping combinations, empty/no-results states and column visibility when affected; do not claim universal table functionality from a static image.
- Dialog sizing, scroll, narrow and desktop layouts, labels, keyboard/focus behavior, errors, loading and retry states. Inspect console/network failures relevant to the journey.
- Financial/document workflows across calculation, persisted record, invoice/receipt rendering and print/export where changed. Verify discounts, tax/freight and totals against actual rules.
- Restriction enforced server-side even if a hidden action is called directly. Recovery from stale state, a concurrent change or upstream failure should preserve data integrity.
- For approval workflows, verify the exact reviewed record revision and media bytes reach publication. Pending edits must not mutate live approved data. List limits must not hide old actionable requests, and mobile comparisons must show proposed values without relying on a page-overflow assertion alone.

Use realistic demo actors and items if a showcase is requested, keep synthetic data isolated and keep credentials private. Explain limitations of stock images, mocked payments and demonstration records. Reuse relevant tests; do not add brittle tests that merely repeat implementation details or rerun unrelated suites without a risk reason.

## Evidence levels and release decision

Keep separate: reviewed source; unit/static checks; contract/integration tests; browser/local runtime; deployed process/config/schema; customer public path; provider sandbox; real financial/delivery outcome; rollback/restore evidence. A skipped platform-specific test remains skipped until run on the supported platform.

For each material finding, record severity/impact, exact scoped evidence, fix, regression result and remaining limitation. Test the original failed journey after a fix. Public DNS/TLS/proxy failure is still a failed customer path even if direct-origin health passes.

Security evidence should identify route/method/actor coverage and untested categories. Aggregate pass counts are supporting detail, not proof that all endpoints, UI states, providers or failure modes work. Resolve recoverable blockers within authorization; ask only for the concrete external action required when useful independent work is exhausted.
