---
name: sre-incident-investigation
description: Investigate production incidents, service degradation, outages, capacity failures, and requests for an SRE root-cause analysis. Use when correlating logs, metrics, traces, Kubernetes/GKE events, traffic, scaling, and dependencies to explain what happened and why. Proactively test the whole failure path rather than limiting the investigation to the user's initial hypothesis or screenshot.
---

# SRE incident investigation

Deliver a causal explanation supported by observations, not a chronology of symptoms. Apply this workflow to the affected service and incident window; deepen the branches the evidence points to. Do not require the user to request each relevant check separately.

## Scope and evidence

- Establish the environment, service, namespace, time zone, onset, baseline, peak, and recovery window. Decode timestamps from supplied dashboard links. Keep time zones explicit.
- Respect the user's operational permissions. Investigation normally uses bounded read/get/query operations. This skill never authorizes production mutations, deployments, restarts, load tests, or messages to other people.
- Inspect existing reports and evidence before querying again. Preserve the query, source, time range, units, aggregation interval, relevant result, and any sampling or query limit for each material conclusion. Keep credentials and customer payloads out of artifacts.
- Make precise causal claims directly inspectable beside the claim. For an event-derived duration or restart reason, include the exact relevant message, event timestamp with time zone, resource identity and event/log identifier. Attach a narrowly scoped raw export and a replay link or read-only retrieval command; a nearby capacity chart is not proof of an event's exact wording or duration. For metric-derived values, retain the query and matching samples; for trace-derived claims, identify the actual spans.
- Keep the evidence needed to review the RCA beside the report, not only in temporary working files or an expiring browser session. If direct evidence is unavailable, label the claim unverified or inferred rather than substituting a related screenshot. Distinguish raw source records, excerpts, UI screenshots and generated visualizations.
- Treat screenshots and proposed causes as starting evidence, not boundaries of the task. Build and test plausible competing explanations. Mark each as supported, contradicted, or unresolved.
- Missing series, failed queries, truncation, and inaccessible sources mean unknown, not zero. Current configuration is not proof of incident-time configuration.
- A query's step is not the source scrape interval. Check collection lag and use event timestamps for precise lifecycle transitions; short scheduling failures can occur entirely between metric samples.

## Demand and actual capacity

Always correlate incoming demand with delivered serving capacity when investigating overload, scaling, or availability:

1. Measure baseline, onset, peak, and recovery RPM/RPS, successes, errors, latency, and timeouts. Break down the dominant routes and callers. Check retry amplification and traffic or rollout changes.
2. Track the complete Kubernetes capacity path: **desired replicas → pod objects created → scheduled onto nodes → initialized/container started → Running → Ready/Available → serving endpoints**. Report observed stages separately. Desired replicas and HPA current replicas do not establish that the cloud supplied capacity. A Running pod may have a restarting or unready container.
3. Verify actual Deployment/ReplicaSet counts, pod phase and scheduling conditions, container state, readiness, and endpoint availability. Include all relevant revisions; establish ownership. Deduplicate redundant scrapes and distinguish active pods from terminating or terminal pods. Do not sum cumulative objects as concurrent capacity.
4. If delivery lags, determine where: controller creation, scheduling, image pull, initialization/startup, readiness, or service endpoint propagation. Pending does not by itself mean insufficient nodes. Inspect FailedScheduling, resource requests/headroom, node readiness, taints, affinity, and relevant storage/network constraints. For image pulls, separate actual pull duration from time including waiting; do not attribute queue time to registry download speed without evidence.
5. For a possible infrastructure capacity shortfall, inspect cluster-autoscaler decisions and node provisioning around the same timestamps, including quota, IP exhaustion, stockout, node-pool limits, and failed scale-up events when relevant. Distinguish using existing nodes from provisioning new nodes, and scheduling from serving successfully.
6. Quantify how long requested capacity took to become scheduled and ready. Do not declare a cloud capacity failure or absolve the provider using replica targets alone. If historical scheduling or provisioning evidence is unavailable, say exactly which stage remains unverified.

Keep observation points consistent: gateway requests, application attempts, and unique business operations are different quantities. Do not add them or subtract them to invent retry counts. A rolling request rate divided by an instantaneous ready-pod count is not measured per-pod throughput. Align windows or label estimates explicitly.

## Failure mechanism and contributing causes

### Deployment configuration review

For every affected workload, explicitly review its deployment configuration as
part of the causal investigation. Compare the incident ReplicaSet's pod template,
the recovery revision, and current configuration; do not substitute today's
Deployment for historical evidence. Retain sanitized excerpts and their resource
UIDs, revision numbers, creation times, image digests, and retrieval times.

- Application and injected sidecar CPU/memory requests and limits; runtime worker
  settings; termination grace period and shutdown hooks. Include pod-level
  admission mutations when the ReplicaSet does not contain injected containers.
- Startup, readiness and liveness endpoint, timeout, interval and thresholds;
  whether they share application execution/dependencies; probe rewriting by the
  service mesh. Distinguish readiness removal from liveness-triggered restarts.
- HPA metric type, target, requests denominator, min/max replicas, stabilization
  windows and scale policies. Check whether application or whole-pod utilization
  drives scaling, and compare configured targets to historical observations.
- Rollout surge/unavailable limits, minimum readiness, PDB selectors and budgets,
  affinity/anti-affinity, topology spread, node selectors, tolerations and node
  pool autoscaling bounds. PDBs do not prevent liveness restarts or guarantee
  capacity during Deployment rollouts.
- Service selectors/ports and mesh routing, retries/timeouts and connection
  limits where relevant. Never dump secret environment values into evidence.
- Establish changes through Git history, retained ReplicaSets, deployment events
  and audit records. Correlate changes with onset and recovery; explicitly mark
  any historical HPA, PDB, sidecar or node-pool settings that cannot be recovered.

Treat each suspicious setting as a testable hypothesis: identify the observed
failure it can explain, competing explanations, and what evidence would refute it.

- Correlate CPU usage and requests/limits with CPU throttling; distinguish throttled scheduling periods from percentage of CPU denied. Check memory pressure/OOMs, process or event-loop saturation, queues, connection pools, and downstream latency/errors where available.
- Separate startup, readiness, and liveness probe failures. Readiness loss removes serving capacity; liveness failure may restart the container. SIGTERM alone does not prove why a process stopped. Verify lifecycle events, exit reasons, and timestamps.
- Inspect application errors and representative slow/failed requests alongside dependency metrics and logs. Check whether suspicious errors existed in the healthy baseline before blaming them.
- Follow trace context where possible. A trace ID in a log is not proof that spans were sampled, exported, retained, or available in the selected source. Report trace coverage limits; do not invent an internal bottleneck from an empty trace view.
- Compare the actual deployed revisions, pod templates, configuration, image digests, scaling policies, and relevant changes with incident timestamps. Recovery following a change supports a hypothesis but does not prove it was the exclusive cause, especially when several changes overlap.
- Separate the initiating trigger, failure mechanism, amplification, contributing constraints, and recovery. A probe restart or HTTP 503 is often a downstream symptom; do not stop there and call the initial root cause established.

## Report and completion gate

Lead with a short explanation understandable to management, followed by the evidence needed to assess it. Include:

- User impact, duration, affected scope, demand/RPM changes, and error/latency changes.
- Requested versus actual delivered and healthy capacity, including whether scheduling/cloud provisioning contributed or remains unverified.
- A compact, time-aligned timeline of traffic, capacity, saturation, lifecycle events, and changes.
- Confirmed causes, probable contributors, and unresolved questions, with confidence proportional to evidence.
- Relevant log/trace examples or an explicit coverage limitation.
- Recovery actions and targeted prevention recommendations tied to observed failure modes, with validation criteria.

For reports with screenshots, verify the delivered viewing experience as well as file existence. Check image paths, rendered images, readable titles/legends, environment and aligned time windows. If the user's Markdown viewer cannot display local images, provide a portable rendered report with embedded images and a clear link to open it; retain the Markdown and raw evidence. Put key event text inline so the claim remains reviewable even without images. Do not claim visibility in a reader that was not tested.

Incorporate recurring user corrections into these decision rules when they generalize to incident review; preserve existing authorization limits and avoid accumulating incident-specific conclusions as universal rules.

Before finishing, ask: **What would an experienced incident commander ask next that this report has not answered?** In particular, verify traffic attribution, actual cloud/pod capacity, dependency behavior, retries, incident-time changes, and why scaling did or did not restore service. Investigate material gaps within existing access and scope; disclose any remaining blocker instead of waiting for the user to notice it. Do not expand into unrelated remediation or claim a fix has been implemented merely because it was recommended.
