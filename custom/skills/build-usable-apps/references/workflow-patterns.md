# Workflow patterns to apply when relevant

These are decision patterns, not a mandatory feature list or legal policy.

## Signup, login and interruption

Specify exactly when a durable account is created. If verified email is required,
enforce proof on the server before creation. Requesting a code, typing one and
successfully verifying it are different events. Disabling the verification
provider must not silently bypass the verification requirement.

For staged registration, a verified draft is one possible design. Choose it only
if the product needs independently saved progress; do not assume it already
exists. Save at explicit boundaries and explain what has been saved. Treat an
unverified draft differently from an authenticated or approved user.

For every save boundary, walk through leaving, session expiry and returning:

| Return state | Useful outcome |
| --- | --- |
| No account yet | Restart or recover the allowed draft without an account-exists dead end. |
| Account exists, details unfinished | Prove identity through an available method, then resume saved details. |
| No password was ever set | Never require a nonexistent password as the only recovery path. |
| Registration complete | Normal sign-in and the product's supported recovery path. |
| Held, deleted or restricted | Explain the supported next step; recovery must not bypass the restriction. |

Handle code expiry, replay, wrong attempts, double submission and concurrent
resends on the server. Consume proof and create/resume the intended account
consistently; failed saves must not strand the user or create duplicates. Return
to the interrupted internal destination after login and reject external redirect
destinations. Do not change an account's role because a returning person used
the other role's signup page.

If password changes/reset are in scope, verify them as real flows. Do not infer
that a security menu or a sentence in documentation proves implementation.

## Forms, defaults and evidence

Document why each required field is needed. Group related information into a
few meaningful steps rather than an arbitrary one-field-per-page wizard. Mark
optional/conditional fields, provide clear upload rules and retain valid input
after errors. A success toast must mean the save actually succeeded.

Prefill known contact/address details. An alternative address for one booking
should not overwrite the profile without an explicit choice. Map estimates,
device geolocation and a user-confirmed location are different facts. Permission
denial and lookup failure need a usable alternative when the task allows it;
late lookup results must not replace a newer address selection.

Keep identity/account numbers as strings and normalize supported presentation
differences at the server boundary. Format/checksum validation does not prove
ownership or government verification. Use the jurisdiction's real rules only
when needed and verify authoritative sources before encoding them.

Protect private evidence with appropriate authorization/storage. Keep it out of
public URLs, analytics, logs, screenshots and example fixtures. Reopen a person's
details intentionally; do not render hundreds of private profiles expanded.

## Approval and later changes

Map one admin decision to the outcome promised by the product. Keep internal
checks visible as a navigable checklist where useful; do not ask the operator
to approve the same business decision on several unrelated screens.

When text and photo/document evidence are both supplied, make comparison easy.
Show a specific correction request with the relevant field/step. Do not add a
second reviewer, repeated reason fields or a separate compliance system unless
the product's verified requirements justify them.

Define which approved fields remain editable. A materially changed reviewed
field needs an explicit correction/review path; ordinary settings should not
reset approval. Compare canonical values so formatting-only changes do not
invalidate valid checks. Preserve unchanged approved evidence and check current
server status even when a browser session is stale. Make account-wide reopening
clear if that is the actual policy; do not imply a field-only permission.

## Mail, notifications and retry behavior

Use a clear pending state and a useful retry countdown for expensive actions
such as sending codes. Enforce duplicate suppression/rate limits server-side;
the button alone cannot protect the service. Allow reasonable human retries
without making refresh or shared networks unusable.

Choose the simplest supported delivery path. Verify the actual sending account,
sender authorization and received headers before claiming a changed sender.
Changing a mail client or TLS port does not itself establish sender permission.
Distinguish queued, provider-accepted, delivered and failed. Operator history
should help diagnose failures without exposing codes or sensitive message bodies.

## Payments and destructive actions

Do not require every service provider to create a payment-platform account when
the business collects into its own merchant account and pays providers later.
Conversely, do not remove provider/legal requirements merely to simplify a screen.
Check the actual agreed model and account capabilities. Keep transaction holds,
refunds and money already paid distinct from a person's account approval.

For deletion, agree on scope: removing access/profile is different from erasing
linked jobs, evidence and payments. If an operator-controlled permanent-delete
flag is requested, enforce it on the server, default it according to the agreed
policy, explain disabled actions, and preserve it during deployment. Showing
“deletable” must use the same effective rules as the action. Do not remove
retention requirements without understanding which ones actually apply.

Use synthetic data for destructive tests. A user request to implement deletion
is not permission to erase production accounts, and an earlier one-time reset
is not a standing reset instruction.

## Production failures and support

Use the simplest observability already available for the problem. When metrics,
logs and traces exist, relate the failing request, time window, release and
dependencies rather than creating disconnected dashboards. Keep contact details,
codes, identity numbers and request bodies out of telemetry; diagnostics must
not undermine the privacy of the workflow being diagnosed.

Verify public browser delivery as well as direct-origin health. A healthy process
can coexist with failed authentication, missing JavaScript or a failing proxy
path. Distinguish a proven recovery from a proven root cause. Test refresh/retry
and shared-network behavior when setting limits; protect expensive operations
without making normal users diagnose infrastructure or request bans removed.
