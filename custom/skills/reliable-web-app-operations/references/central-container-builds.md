# Central CI/CD and container build contracts

Use when service teams should own application declarations while a platform or
ops owner maintains the build pipeline. Keep actual service names, registry
visibility, provider credentials and deployment topology in project configuration.

## One platform, explicit app inputs

Keep reusable workflows, Docker build definitions, validation and publishing logic
with the platform owner. Each app can declare its versioned build/runtime contract
in a root manifest: schema version, stable service ID, supported build profile,
package/build paths, artifact output, port and health path, worker entrypoints,
and required configuration key names. Secrets are references, never values.
Keep placement, private host addresses and cluster settings in the agreed topology
authority; link it explicitly rather than maintaining two editable copies.

A generic Dockerfile can use reviewed profiles for genuinely different runtimes.
Do not force every framework into one fragile shell branch, or quietly introduce
per-app pipeline copies when centralized ownership is the requirement. New profile
needs should be reviewed in the platform contract with representative app tests.

Validate manifest types, paths and supported values before fetching/building or
mutating deployment state. Do not interpolate manifest strings as shell code.
App install/build scripts execute source code even with a validated manifest:
keep release-write and deployment credentials out of that execution environment.
Pass source/registry credentials through scoped mechanisms that do not persist
in image layers, build arguments, logs or archived source.

## Build and deployment are separate responsibilities

Document the actual executor: local workstation, isolated CI runner or a dedicated
builder. Building on the serving VM consumes its disk/CPU and introduces source
access and tooling there; do not imply it is necessary for deployment. A normal
deployment can pull a verified image digest using only ops configuration and
required DB tooling. Temporary checkout cleanup alone does not prove credentials
or application source are absent from caches and artifacts.

Bind the selected source commit, app version, manifest, platform build revision,
base image and resulting image digest in release evidence. For a human-readable
`appVersion-commitId` tag, obtain the abbreviation from Git on the selected source
commit; retain full revisions and digests for identity. Tags are not immutable
deployment evidence. Read [release-versioning-and-hotfixes.md](release-versioning-and-hotfixes.md)
for version calculation and [portable-deployment.md](portable-deployment.md) for
promotion without rebuilding.

For example, `git log -1 --format=%h <selected-source-commit>` asks Git for the
abbreviation of the revision actually being built. Do not hardcode seven/eight
characters or accidentally query the ops checkout's HEAD. Verify the result
against the selected full source revision and retain the digest for deployment.

## Measure size and verify the runtime

- Use staged builds and copy the needed runtime output. Keep source caches, test
  artifacts and build-only dependencies out of the final image where possible.
  Compare compressed registry transfer size separately from local unpacked size;
  record platform/architecture and measurement method.
- Framework tracing or standalone output can omit worker, migration, template,
  native-library or dynamically loaded dependencies. Verify each shipped process
  from the final image without sibling checkouts or development bind mounts.
  Do not restore an entire development dependency tree merely to hide a missing
  runtime dependency; establish and test the actual dependency closure.
- A hardened base, Docker Hardened Images (DHI), distroless or shellless runtime
  is a candidate, not a security certificate. Verify the chosen image's current
  availability, licensing/access, supported runtime/platform and update policy
  from authoritative documentation when selecting it. Record the actual base
  digest; do not describe an ordinary base as hardened because of its tag.
- Test non-root execution, the intended filesystem permissions, narrowly writable
  paths, dropped capabilities and read-only root filesystem where compatible.
  A shellless image needs a compatible entrypoint and health probe, not a command
  that assumes `sh`, `curl` or a package manager exists. Test shutdown and worker
  execution as well as HTTP readiness.
- Preserve dependency/provenance evidence and assess relevant vulnerability scan
  findings. Smaller size, no shell or zero reported advisories alone does not
  establish application security. Use the service security/QA guidance for access
  control and actual customer workflows.

## Registry visibility and disk cleanup

Inspect final image contents for credentials, personal AI configuration and private
files before publication. Public registry access is a separate explicit decision;
never switch visibility automatically to bypass a private-repository quota.

Remove task-owned temporary checkouts and credentials after use. Scope cache/image
cleanup to the builder and retention policy, coordinating with concurrent builds.
Preserve active and known-compatible rollback images, volumes, backups and failed
release evidence. Do not apply an indiscriminate system/volume prune to a shared
host. Measure disk reclaimed and remaining capacity without claiming all caches
were removed when some are deliberately retained.

Keep local build tests, final-image runtime tests, registry publication, deployed
digest, public customer flow and rollback evidence separate. Reusable guidance
does not establish that any specific project passed these checks.
