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

## Hosted payment failures

A provider-hosted failure screen proves that checkout reached the provider; it
does not identify who caused the failure or whether money ultimately settled.
Correlate the application's order/link with every provider payment attempt and
the webhook history. Re-fetch final state before advising another payment because
a failed or delayed event can be followed by capture.

Retain only bounded support categories from the provider's structured attribution
fields, such as customer timeout, issuer bank, merchant integration, gateway,
provider or unknown. Do not expose raw descriptions, request objects, payment
identifiers, bank references or customer data in ordinary UI or telemetry. Keep
the link lifecycle separate from the attempt lifecycle: one active link may have
several failed attempts and a later successful one. A failed attempt must not be
shown simultaneously as “confirmation pending.” Test both the correct recovery
message and absence of contradictory status copy.

Separate these conclusions in the incident record: application request health,
provider attribution, captured/refunded state, customer-reported debit and bank
reversal. `captured=false` is not merchant receipt; a reported debit still needs
secure UTR/RRN reconciliation before a merchant refund is promised or initiated.
