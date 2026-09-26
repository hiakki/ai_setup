# Reusable Engineering Playbook

Project-neutral lessons originally collected in Elvique, centralized on
25 September 2026. Detailed guidance travels with each skill in `custom/skills/`
and its global installation; application specifications remain in their projects.

## Choose the relevant skill

| Work | Primary skill | Add when relevant |
| --- | --- | --- |
| Setup, deployment, environment, monitoring and provider delivery | [reliable-web-app-operations](../custom/skills/reliable-web-app-operations/SKILL.md) | SRE, security or database expertise |
| Forms, admin workflows, tables, selectors, uploads and permissions | [build-usable-apps](../custom/skills/build-usable-apps/SKILL.md) | Frontend, accessibility or browser testing |
| Money, status, eligibility, hierarchy, corrections and historical documents | [auditable-business-workflows](../custom/skills/auditable-business-workflows/SKILL.md) | The actual domain, billing or database specialist |
| Active incident and causal investigation | [sre-incident-investigation](../custom/skills/sre-incident-investigation/SKILL.md) | Relevant service or infrastructure expertise |

For work across several areas, begin with the highest-risk behavior and load only
the additional guidance needed. Skills support the user's chosen task and existing
permissions; they do not authorize deployments, restarts, payments or publishing.

## Merge decisions

`operational-admin-ux` was merged into `build-usable-apps`: both guide application
workflow and operational UI work. Its tables/selectors, forms/uploads and
permissions/audit references are preserved and linked for selective reading.
No second skill or compatibility alias is installed under the former name.

Operations remains separate from SRE investigation. The former designs the release
and telemetry path; the latter establishes causes using incident evidence.
Combining them would bring unnecessary deployment instructions into read-only RCA.

Auditable workflows remains separate from UI and operations. It governs source
facts, derived values, rule versions, corrections and historical snapshots across
all consumers. A UI change need not load that domain guidance unless its business
behavior requires it.

## Lessons preserved

1. Fix demonstrated shared causes across equivalent controls and consumers before
   claiming a global correction.
2. Separate source facts, derived values, projections and settled outcomes.
3. Treat referral, placement, access, participation, contribution, propagation and
   earning as distinct policies where the approved domain model uses them.
4. Distinguish provider acceptance, delivery and completion.
5. Preserve recoverable operator input and explicit deployment environment values.
6. Verify the changed workflow after build or deployment; health alone is insufficient.
7. Distinguish browser/network, proxy, application, storage, host and provider failures.
8. Keep realistic demo/test data isolated at the shared reporting boundary.
9. Make corrections explicit, impact-aware, authorized, atomic and auditable.
10. Keep reusable guidance project-neutral and business rules in project specifications.

## Install and maintain

Use the [custom skill catalog](../custom/skills/README.md#install-and-use) to install
the collection or share a complete individual folder. Supporting references install
with their skill. The `custom` component discovers these folders automatically on
macOS, Ubuntu/Debian and native Windows; no provider payload is vendored here.

Update the maintained source in `custom/skills/`, validate its frontmatter and
links, then reinstall within the authorized scope. Preserve local edits if the
installer reports a conflict. Keep implementation, local checks, provider tests,
deployment and live completion as separate evidence levels.
