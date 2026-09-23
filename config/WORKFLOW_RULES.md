# Finish the user's workflow

- Treat recoverable blockers as part of the task: investigate the cause, implement the simplest reliable fix or remove an unnecessary dependency, and retry the actual user workflow before stopping.
- Do not hand back an "unavailable" or "blocked" message while useful, authorized debugging or recovery remains. Passing tests and deploying code do not establish that the requested end-to-end outcome works.
- Prefer simplifying the existing automated path over adding layers, mandatory providers, or manual operator steps. Preserve the requested quality, factual accuracy, security and publication controls; never conceal a failure with degraded output or a false success.
- If completion truly needs credentials, additional resources, spending approval, or another external action, identify the concrete cause, the recovery attempts already made, and the smallest user action required. Continue independent work instead of abandoning the task.
- For automated production tasks, make the application perform the work, exercise it through its normal flow, verify its output, and only then report completion.

# Response brevity

- Do not over-explain simple things. When a longer explanation is necessary, end with short bullet points summarising all key points in as few words as possible.

# Provider integrations and release evidence

- Verify the actual customer's provider account capabilities, product eligibility, credentials, webhook configuration, and settlement model before choosing a mandatory integration dependency. Valid API keys do not prove access to every provider product.
- Research official provider documentation and simpler supported alternatives proactively. Do not make the user discover basic integration options or diagnose avoidable architectural blockers.
- For marketplaces, distinguish customer collection, merchant settlement, commission accounting, refunds, and partner payouts. Do not require a split-payment product for collection unless the chosen business flow actually needs it. Never imply that a payment link automatically pays a partner.
- Preserve explicit operator settings during deployment. Do not silently force enablement flags or interpret an application approval flag as provider approval. Verify the environment of the actual running process and explain any intentional override before deployment.
- Do not release an online-only workflow with collection disabled as a usable paid-booking launch. Check that every required step in the customer and provider journey has a working path.
- Report implementation, mocked/unit tests, sandbox provider tests, deployment, live provider verification, and full end-to-end completion as separate evidence levels. A build, mocked payment, HTTP 200, or deployment is not proof of a successful financial transaction.
- Exercise the real provider through the application's actual SDK, request payload, response validation, and browser flow. A separate capability probe or documentation-shaped simulator can miss failures in the implemented integration; add regressions for real contract differences. Do not send empty optional objects merely to satisfy inaccurate SDK types; adapt the type at the SDK boundary and verify the actual provider contract.
- A financial review hold needs an audited resolution path. Preserve money already sent, distinguish recovery from refund, and ensure an operator can reconcile legitimate outcomes without editing the database.
- Before claiming payment readiness, verify the real application journey: agreed amount, payment confirmation, duplicate/replayed events, extensions, cancellation/refund races, commission, payout eligibility, and reconciliation. Mark every untested or externally blocked step explicitly; never hide it behind an aggregate passing-test count.
- Treat UI correctness, public URL availability, performance, authentication, and recovery behavior as release checks, not optional user-discovered issues. A direct-origin pass does not erase a public-path failure.
- Migration history is not proof of the live database schema. Verify required columns, tables, and financial constraints against the application's actual database connection before switching a release, then exercise a real webhook or affected query. Repair drift with reviewed, additive migrations; never conceal it with automatic migration baselining or destructive schema synchronization.
- If provider approval or a user-controlled payment is required, finish all independent implementation and verification first, then identify the smallest remaining action. Never fabricate live payment evidence or mark unresolved money movement as complete.
