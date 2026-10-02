# Release versioning and hotfixes

Use when auditing or implementing release automation. Keep project names,
credentials, run IDs and current rollout status in the project's runbooks.
This reference does not authorize a release, merge, schedule or deployment.

## Establish what actually increments

Trace the committed package version through the versioning tool, image builder,
release record and deployment selection. Reading or validating a version does
not increment it. A changing Git suffix is not an app version bump. Check actual
history around a fix/feature and run the normal publisher's preview.

Define independent service versions, the public compatibility contract and a
pre-1.0 policy. In a Conventional Commits workflow, compatible fixes normally
increment patch and features minor; breaking changes need an explicit pre-major
rule. Commit labels are intent, not proof of compatibility. Do not bump for
unchanged-code retries or deployments. Separate platform-only rebuild identity
from application versions. Release tools are preferable to a custom SemVer engine.

When the project requires central ownership, keep the pinned release tool,
configuration and workflows in the ops owner. App repos receive ordinary version,
lockfile and changelog changes. Verify a supported cross-repo interface rather
than copying pipelines into every app. A PR merged in another repo does not
automatically trigger the central workflow: explicitly configure an authorized
schedule/event integration or document manual dispatch.

## Bootstrap and publication

- Record the real existing package version and history boundary. Do not invent
  past GitHub releases or reset versions merely to onboard automation.
- Distinguish an initial version override from a previous-version baseline.
  With Release Please, `bootstrapSha` limits history; `initialVersion` alone is
  not a commit-derived bump. Verify the pinned library's first-release behavior.
- Decide how apps with packaging-only history establish their first formal
  release. Keep any bootstrap exception explicit and separate from later rules.
- Compare initial changelogs against a real commit when no earlier tag exists.
- A merged release PR changes the package before its tag is published. Preview
  that pending publication before calculating another release PR.
- Preserve approval boundaries: generating a PR, merging it, publishing its tag,
  publishing an image and deploying it are separate actions.

## Make a multi-repository release candidate reviewable

Before merging, publishing or deploying a multi-repository product for a production defect,
create one ops-owned release-candidate directory with a stable identifier such as
`RC-YYYYMMDD-NNN`. Keep a machine-readable JSON or YAML manifest as the authority
and generate the human-readable HTML review from it; do not maintain a second
hand-edited release description.

The candidate manifest should record:

- the actually deployed production version and immutable digest of every app;
- each affected app, its exact source revision and its calculated next version;
- the owning repository's versioned `CHANGELOG.md` path;
- bounded paths to issue reproduction, current screenshots and the regression's
  before-fix failing output, plus what prior coverage missed;
- the proposed pull requests/commits, required final checks and candidate status;
- approval identity/time and the exact candidate hash once approval is granted.

Keep implementation, changelogs and regression tests in their owning app
repositories. The ops repository retains only cross-app coordination, references
and review evidence. Before-fix evidence must demonstrate the reported failure;
post-fix checks are separate and must not overwrite it. Redact secrets, customer
data and provider identifiers from evidence.

Use an explicit state transition such as `draft` → `approved` → `deploying` →
`released` or `failed`. CI/CD must reject a draft, an incomplete manifest, a
candidate whose source/configuration/evidence changed after approval, or a
generated HTML view that is stale relative to the manifest. Define what approval
authorizes for the target product. If one approval covers merge, build, publish
and deployment, record that scope explicitly; never infer it from a comment or
from an application/business approval flag.

## Provenance and credentials

Bind published release tag → resolved commit → committed package version →
image digest. A release's `target_commitish` can be a moving branch; resolve its
tag. Recheck tag identity before archiving. A released commit may be behind main;
do not accidentally build newer main code or relax unrelated ops trust checks.

Use Git's abbreviation command (for example `git log -1 --format=%h` on the
selected commit) when the project wants a short commit suffix. Do not assume a
fixed seven/eight-character length. Retain full source and platform revisions
and immutable digests in provenance. Rebuilding the same tag with newer tooling
can produce a different digest; exact rollback uses the recorded prior artifact.

Treat later promotion as a separate deployment operation, with no app-version
bump or implicit image rebuild. Preserve both the original build provenance and
the current deployment executor/configuration identity. Read
[portable-deployment.md](portable-deployment.md) when implementing retained-artifact
promotion or selecting between VM and cluster backends. The existence of a
promotion workflow does not imply isolated maintenance-branch hotfix support.

Keep repository-write credentials confined to release orchestration. Do not
expose them to app installation/build scripts, image layers or the deployment VM.
Keep source-read, registry-write and deployment identities separately scoped.
Verify capability through the actual provider workflow; secret presence alone
does not establish cross-repo permissions. Do not upload personal CLI credentials
as CI secrets to bypass missing dedicated credentials.

## Expedited release versus isolated hotfix

An immediate run on main is an expedited normal release. If main contains
unreleased features, a `fix:` commit can ship those features too. Do not call
that an isolated production patch.

For a requested isolated hotfix:

1. Identify the artifact actually running, its source SHA, config and compatible
   schema; the newest published tag may never have been deployed.
2. Branch from that source. Review only the intended fix and dependency changes.
3. Scope version calculation to the maintenance line. A patch on an older line
   may be numerically below main's newest release; retain global tag uniqueness
   while checking monotonicity within the selected line.
4. Select that explicit release for build/deploy. Avoid changing the default
   "latest" release to an older maintenance line unintentionally.
5. Keep branch/tag provenance, tests, approval and deployment checks. If main
   ancestry is a current guard, replace it with an explicit trusted-track check;
   do not remove source verification to make a hotfix pass.
6. Forward-port the code fix to main without downgrading its package version or
   blindly copying maintenance release metadata. Track that follow-through.

Document support as implemented, verified or planned. If a pipeline is hardcoded
to main, mark isolated hotfixes unsupported until branch selection, version
calculation, publication and source validation all support the chosen track.

## Provider failures and proof

Retry transient failures with bounded backoff through reconciliation, not blind
write replay or another version bump. Fail closed on permission and policy
violations. Provider writes can succeed before the response or PR metadata update
fails: inspect published tag/SHA and remaining pending state before recovery.

Observed with Release Please 17.11.2: the SDK may repair PR labels but still throw
`DuplicateReleaseError`; its error `tag` field can contain the literal `tagName`.
Recheck the installed version before adopting a workaround. Accept recovery only
after independently matching all intended published, non-draft tags and SHAs and
confirming no pending release remains. Never suppress arbitrary duplicate errors.
Log safe failure category/status, not token-bearing SDK request objects.

Useful checks: first/subsequent patch/minor/breaking releases; no-op retries;
merged-but-unpublished preview; package/lockfile agreement; moved tags; auth
denial; bounded provider failure; partial-write recovery; production hotfix with
unrelated main features; older maintenance line versus newer main; code forward-port.
For a review-gated multi-app fix, also test incomplete manifests, preserved
before-fix evidence, stale generated HTML, approval invalidation after any candidate
change, and rejection of CI/CD before approval.
Use the pinned tool for version tests. A mock duplicate should match the actual
SDK contract. Record local tests, real PR creation, tag publication, image/digest
verification and live deployment separately. Documentation-only updates need
link/consistency checks, not a service restart.

Sources: [SemVer](https://semver.org/),
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/),
[Release Please CLI](https://github.com/googleapis/release-please/blob/main/docs/cli.md),
[Release Please bootstrap](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md).
