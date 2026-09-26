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

1. Record impact, start time, affected journey, environment, and release.
2. Confirm telemetry freshness before trusting empty charts.
3. Correlate external, proxy, app, storage, host, and provider evidence.
4. Reproduce through the same customer path when safe.
5. Apply the smallest reversible containment only within explicit operational authorization; otherwise present the proposed action and its verification plan.
6. Verify recovery through both health signals and the affected workflow.
7. Record root cause, detection gap, prevention, and owner.

