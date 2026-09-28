# Separate extraction, containers and CI/CD into verified stages

Use this sequence when the user wants to split a running application and then
containerize it. Honor the selected build machine, registry and rollout order.
Do not turn service extraction into simultaneous runtime, container, registry and
CI migrations. A failure becomes harder to diagnose when all four change together.

This is a sequencing rule, not evidence that a particular application has passed
the stages. Existing working automation may remain in use; do not dismantle it
merely to follow this example. If the user selects another sequence, record it.

## 1. Extract directories and run ordinary processes on the target VM

- Put each agreed domain in its owning directory/repository. Preserve API,
  transaction, authentication, payment and private-data boundaries.
- Provide the smallest repeatable build/start/stop/status scripts or process
  definitions. Start each service from its declared inputs and explicit environment;
  do not copy the entire legacy environment into every process.
- Run and verify the extracted services on the authorized VM before introducing
  a new container delivery path. Keep source checkouts there temporarily if this
  stage requires them, even when the final goal is an image-only application host.
- Prove dependency independence from an isolated source archive outside the
  monolith's directory tree. A nested service can silently resolve undeclared
  packages from a parent's `node_modules`, including type-only UI dependencies.
  Clean-install, typecheck, build and exercise the archive without parent mounts;
  remove accidental dependencies or declare genuinely required ones explicitly.
- Verify SHA-256 at each artifact handoff. A local file, a container bind mount
  and a transferred file can expose different bytes during filesystem problems.
  If hashes disagree, stop before executing or installing; copy the exact file
  through another authorized path and verify again. Do not diagnose a universal
  Docker bug from one mismatch or treat matching filenames as matching content.
- Bind archive contents to the requested source revision before naming a release.
  A checksum proves byte identity, not the claimed Git commit. Verify the Git
  archive commit header or an equivalent trusted manifest. Exclude personal agent
  tooling and generated outputs explicitly at archive creation; preserve source
  files and do not relax traversal/symlink checks to accommodate unrelated inputs.
- If Git object/ref reads disagree across an authorized container bind mount,
  verify the local commit and remote ref independently. A checked Git bundle copied
  into a temporary isolated repository can provide a consistent transfer without
  rewriting history. Verify the remote SHA afterward; never force-push merely to
  bypass an unexplained object-type or missing-tree error.
- Exercise the actual cross-service journeys, denied access, writes, uploads and
  workers. Compare behavior with the known working application and verify recovery.
- Verify rollback environment removal as well as restoration. Process managers
  may merge new environment variables on restart instead of deleting keys absent
  from the old configuration. Preserve private launch metadata, use the manager's
  verified replacement semantics, and inspect the actual listener environment.
  Never print environment objects or secret-bearing assertion diffs to prove it.
- Before switching a process working directory, inspect its configured log,
  cache and temporary paths. Ignored runtime directories are absent from clean
  source artifacts. Prepare their owned directories or explicitly relocate them
  before restarting; a healthy candidate does not prove an existing process
  manager can launch it with historical metadata. Test the rollback independently.
- Preserve explicitly configured public frontend settings through a reviewed
  allowlist at both build and runtime. Do not copy backend environments into a
  frontend to preserve branding, public-launch or pricing display settings.
  Browser-bundled variables may be fixed at build time; runtime injection alone
  is not evidence that the rendered value changed.
- For multiple frontend applications sharing one origin, verify public page
  ownership, asset prefixes and full navigation across application boundaries.
  Exercise the assembled release through the actual gateway, including client
  navigation and image optimization. A fixture proxy's path rewriting can conceal
  a mismatch; compare its rules with the deployed gateway and current framework.
- Test side effects required for operation, not only response status. An image
  optimizer can return a valid image while failing to persist its cache under a
  read-only release. Keep service-owned caches outside immutable source, verify
  actual writes and inspect logs without making the whole release writable.

**Exit:** the separated application works through its normal public entry point
using ordinary commands/scripts. Empty repos, copied modules, individual health
responses or a design document do not satisfy this gate.

## 2. Build images on the chosen local machine and push to the registry

- After stage 1 passes, package the working services. If the user chooses a Mac
  and Docker Hub, build there and push to the authorized Docker Hub namespace;
  do not silently substitute a VM builder, GHCR or GitHub Actions.
- Match the target VM's architecture explicitly, especially for Apple Silicon
  building Linux amd64. Test native libraries, runtime assets and signal handling
  in the final target-platform image.
- Prefer compatible free/public minimal bases, multistage builds and non-root
  runtimes. Use shellless images where dependency closure permits. Pin digests,
  exclude credentials and build tools, measure size and inspect vulnerabilities.
  Do not call an image hardened or shellless without inspecting the final result.
- Push identified source revisions/versioned images; verify the registry digest.
  Free/public base images do not authorize public publication of private application
  images. Confirm destination visibility and account capabilities at this stage.
  Image publication is distinct from deploying it.

**Exit:** all required final images work, have recorded source/digest identities
and can be retrieved from the selected registry. No CI platform is required yet.

## 3. Replace VM application processes with Compose and verified images

- Use the already verified images in Compose. Keep durable data, secrets, uploads,
  backups and environment configuration outside replaceable containers.
- Switch carefully, with compatible schema, one active scheduler/ownership
  arrangement per job, coordinated worker handover and a rollback path. Multiple
  workers may run where the application's concurrency model supports them.
  Verify the same actor journeys again through the public route.
- Only then remove superseded application code/checkouts after checking process
  paths, mounts, timers and recovery dependencies. Retain the requested parent
  workspace and any explicitly needed operations/database-operations checkouts.

**Exit:** the Compose deployment works with the published images and does not
depend on the retired application source directories. A successful `compose up`
alone is insufficient.

## 4. Automate the proven process with GitHub Actions

- Design CI/CD around the build, test, publication and deployment commands already
  proven in stages 1–3. Automate that process instead of discovering architecture
  while provisioning runners, registry credentials and signing infrastructure.
- Add scoped credentials, trusted/untrusted job separation, release identity,
  concurrency, cleanup and recovery appropriate to the actual account and host.
- Exercise a real workflow from source change through deployment and verification.
  Do not mistake workflow YAML or a passing platform unit test for working CD.

**Exit:** automation reproduces the working manual release and its verification.

## Correcting an out-of-order attempt

If work has jumped ahead, state the current evidence, defer unfinished later-stage
work and return to the earliest unmet gate. Stop scheduling new out-of-order jobs;
do not erase useful changes or stop unrelated services. Record the selected order
and per-stage status in the application's own migration document. Keep this shared
reference generic and never copy application credentials or private infrastructure.
