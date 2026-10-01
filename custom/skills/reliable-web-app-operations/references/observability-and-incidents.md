# Observability And Incidents

## Layered Signals

Correlate rather than guess:

| Layer | Useful signals |
| --- | --- |
| Browser | navigation timing, Core Web Vitals, failed resources, client errors, network type |
| Edge/proxy | status, upstream latency, request ID, TLS, connection failures |
| Application | normalized route latency, status class, event-loop delay, memory, structured errors |
| Storage | operation latency, size, rows, lock/contention failures, backup age |
| Host | CPU, available memory, swap, disk, inodes, process restarts |
| Synthetic | external availability and response time from more than one location |

For a report that “the website is slow,” first separate one-user network/device problems from broad service degradation. Compare external probe latency, server latency, browser timing, host saturation, storage latency, and deploy time.

## Telemetry Safety

- Strip query strings and normalize dynamic paths.
- Allowlist fields before export.
- Do not export passwords, OTPs, cookies, authorization values, request bodies, KYC, bank, payment, or contact data.
- Keep metric labels bounded. Avoid arbitrary URLs, request IDs, exact errors, and customer identifiers.
- When per-account operational metrics are explicitly required, use an access-controlled identifier, expire inactive series, constrain dashboard defaults, and document the privacy/cardinality trade-off.
- Deduplicate request instrumentation by request ID only within a short bounded window; reused IDs must become countable after expiry.

## Dashboard Semantics

- A stat or gauge should use an instant query when historical range evaluation would produce stale entries.
- Avoid `rate()` for a just-created per-identity series when the first event must be visible before a zero baseline exists. A bounded rolling gauge may be more honest.
- Filter inactive zero-value identities from rankings.
- Do not default a selected-user chart to every user over a long range.
- Put a concise definition and time window in each panel description.

## Incident Workflow

### Cost and configuration evidence

Before endorsing an observability migration's cost, measure ingest shape and
background work as well as stored bytes: batch frequency, physical write targets,
derived writes, merging, active replicas and representative queries. Separate
live debugging, hot search and archive needs. Verify which billing dimension an
optimization changes; a revised estimate is not measured savings.

Before applying desired configuration, compare source, selected release inputs
and effective runtime state. Identify intentional out-of-band changes and their
owners, then review the planned diff. A stale checked-in production file is not
evidence of current deployment. Drift alone does not prove incident causality.

### Investigation steps

1. Record impact, start time, affected journey, environment, and release.
2. Confirm telemetry freshness before trusting empty charts.
3. Correlate external, proxy, app, storage, host, and provider evidence.
4. Reproduce through the same customer path when safe.
5. Apply the smallest reversible containment only within explicit operational authorization; otherwise present the proposed action and its verification plan.
6. Verify recovery through both health signals and the affected workflow.
7. Record root cause, detection gap, prevention, and owner.

## Healthy APIs, Broken Browser

When dashboard APIs and queries succeed but panels or plugins fail, inspect the
actual signed-in browser's network and console before reinstalling a datasource.
Compare the failing asset through the public proxy and direct origin: status,
complete byte count, hash and a cache-busted request. Include a throttled download
when failures depend on response size or client speed. A successful response
header does not prove a complete response body.

If a buffered proxy response is truncated, inspect the effective worker identity,
temporary-directory permissions, disk/inodes and persistent proxy error log.
Transport errors alone do not identify the cause. Choose an authorized,
route-scoped repair: correct the temporary storage ownership or deliberately
change buffering for the affected route after considering resource behavior.
Do not disable buffering everywhere or weaken filesystem permissions by default.
Validate, reload only the affected service with permission, then repeat both the
download and the real browser journey. Logs attached to a dead terminal are not
durable incident evidence.

## Collector Readiness Is Not Telemetry Completion

Verify each boundary separately:

1. The collector's readiness and scrape endpoints respond.
2. A labelled synthetic event is accepted, queryable and displayed.
3. A real request through the production-built application emits a safe event.
4. The event and sampled trace correlate through the configured exporters.
5. The actual public customer path and intended deployed release are verified.

A readiness endpoint can succeed while ingestion fails, for example during a
disk/WAL safety shutdown. Inspect write responses, dropped/export-failure metrics
and disk capacity. Do not raise production safety limits just to pass a test.
Keep synthetic records distinguishable from customer activity. A collector smoke
test does not establish that an unrestarted application emits instrumentation.

Assign one intentional owner and destination for each host metric, log and trace
stream. Do not leave a cloud agent exporting the same signals as a self-hosted
Prometheus/log/trace stack without an explicit requirement, cost decision,
retention policy and verified IAM. A misconfigured duplicate exporter can drop
everything while generating enough retry logs to consume the host disk. When
retiring it, stop and disable it first, verify the retained telemetry path, then
remove the package and its own residual files; do not infer retained coverage
from the replacement collectors merely being ready.

Make application telemetry opt-in where the deployment contract requires it.
Preserve operator settings and separate monitoring provisioning from app rollout.
Validate effective in-container configuration after updates: atomic file replacement
can leave a single-file bind mount pointing at an old inode. For mutable config,
consider a directory mount or explicit container recreation; confirm ownership and
readability under the actual container UID. Keep secret access least-privileged.

For containerized system-journal readers, mounted files and a healthy component
do not prove ingestion. Check a labelled synthetic host journal entry, the reader's
line counter, its actual UID/groups, and the correlated backend query. Default
local-machine discovery can miss mounted host journals; use an explicit mounted
journal directory when supported and verify against the installed collector
version. In an Alloy v1.19.2 runtime check, default discovery read zero lines while
an explicit directory produced correlated logs and traces. This does not establish
the right path for every host: verify persistent versus volatile journal storage
and retain exact unit/identifier filters. Do not collect the whole system journal
or grant applications extra permissions to compensate for a collector mistake.

## Remote Diagnostic Endpoint Acceptance

Treat a remote diagnostic or MCP connection as four separate gates: the active
ingress route, the public adapter's enablement/credential/expiry policy, matching
read authority on every downstream owner, and the client's credential lookup.
Inspect the running proxy process arguments before selecting a configuration path;
validating a retired checkout or the proxy's default path creates false evidence.

For clients that accept a `bearer_token_env_var` setting, supply the environment
variable's **name**, not the token value. Keep the value in the platform's secret
store and effective process environment. Registration success and `tools/list`
still do not prove useful diagnostics: call one adapter-local tool and at least one
tool from each downstream owner family. The same sanitized error fingerprint across
otherwise unrelated owner tools is evidence of a shared boundary failure such as
disabled owner policy, stale authority URL or credential mismatch. Align and rotate
the bounded read credential together, verify every real tool call, then remove
temporary transfer files. A successful diagnostic read is operational evidence,
not proof that the observed business or provider workflow succeeds.

## Safe Correlation And Failure Behavior

- Instrument the actual framework/runtime path. A vendor-specific header hook
  that works on managed hosting may not run on a self-hosted deployment. Verify
  correlation through real HTTP requests and concurrent request isolation.
- Treat incoming correlation IDs as untrusted: validate length/format or replace
  them, and never use them for authorization. Keep IDs out of metric and indexed
  log labels; use structured log metadata and traces for correlation.
- Inspect all exporters, automatic spans and resource attributes. A sanitized
  custom span does not make a second automatic exporter safe. Verify with synthetic
  query/header/body canaries without using real secrets or customer data.
- Bound asynchronous telemetry queues, event sizes, files, retries and retention.
  A telemetry failure must not change a successful business outcome or conceal
  its original exception. Surface dropped events, failed writes and exporter
  initialization errors through an independent, rate-limited diagnostic path.
- Document sampling honestly. Head sampling does not guarantee an error trace;
  keep safe error events separately and avoid links to traces never exported.
- Check environment parsing against the installed SDK and effective process.
  A configuration-shaped unit test is not evidence of runtime enablement.
