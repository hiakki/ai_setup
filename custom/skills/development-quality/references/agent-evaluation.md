# Agent and skill evaluation

Use Promptfoo as the comparison/report runner. Evaluate the actual coding CLI,
not a chat completion pretending to be an agent. The central `evaluations/quality`
directory contains a six-case pilot, CLI provider and independent graders. It is
also distributed inside `~/.local/share/ai-setup/quality/evaluations/quality`.

1. Freeze the task, inputs, provider/model version, permissions, skill revisions
   and machine/browser details. Compare baseline and candidate in separate fresh
   workspaces. Do not change prompts and models at the same time.
2. Review the six cases: seeded bug, behavior-preserving refactor, responsive
   screen, source-grounded lesson retrieval, irrelevant-skill avoidance and tool
   failure recovery. Adapt synthetic tasks to representative authorized work.
3. Run `promptfoo eval -c /absolute/path/promptfooconfig.yaml --no-cache
   --max-concurrency 1 -o /absolute/path/ignored/results.json` only after checking
   provider authentication, model budget and execution scope. Set
   `AI_SETUP_RUN_AGENT_EVALS=1` deliberately; otherwise the provider refuses calls.
4. Use existing `codex` or `claude` CLI login. The harness never reads a repository
   `.env`, prints credentials or calls Hindsight reflect. Claude/Codex runs can
   consume subscription quota or billable usage; installation is not a free run.
5. Grade actual files and independently executed checks. Skill reads in a trace
   are supporting evidence, not proof that the agent applied the skill correctly.
   Do not award success for output containing “passed”. Agent-written tests alone
   are not the oracle. The responsive case has static checks; complete visual,
   keyboard and responsive browser checks separately before claiming UI quality.
6. Keep raw traces locally in the ignored result directory. Review before sharing.
   Record failures/timeouts as failures, never drop them from the denominator.
   Score task correctness first, then regressions, evidence, elapsed time and
   tool/token cost where the provider reports it. Do not estimate unknown cost.

The shipped harness tests the active user configuration. For a controlled
before/after test, use separately provisioned authorized user homes with the same
authentication and explicitly selected skills/rules. A task prompt alone does
not isolate global configuration. Record the actual configuration revision in
`AI_SETUP_EVAL_LABEL`; never claim a current-versus-candidate comparison from a
single run. Repeat fresh runs before assigning stable product scores.

Upstream references: [coding agents](https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/),
[agent skills](https://www.promptfoo.dev/docs/guides/test-agent-skills/),
[Python providers](https://www.promptfoo.dev/docs/providers/python/).
