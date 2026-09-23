---
name: laya-decisions
description: Use the configured Laya service for bounded semantic classification, scoring, or selecting among a supplied shortlist of skills or handlers. Use for Laya requests or repeated typed decisions where a small model may save work.
---

# Laya decisions

Use the globally configured remote service through the helper; no local model,
SDK install, or project setup is needed. The Python standard library is sufficient.

Prepare a small JSON request with `state` and a `questions` object. Each named
question has `instructions` and one of these types:

- `choice`: `criteria` is an object mapping candidate IDs to descriptions.
- `score`: `criteria` is an ordered list of labels, indexed from zero.
- `noul`: a yes/no question; no criteria required. The answer is a probability,
  not a Boolean.

Run from any project:

```bash
python3 ~/.agents/skills/laya-decisions/scripts/predict.py --input /path/to/request.json
```

Or pipe JSON to that command without `--input`. The helper emits the server JSON
on stdout and elapsed milliseconds on stderr. It exits nonzero on errors and
does not retry or switch providers automatically. Default timeout is 30 seconds;
`--timeout 60` allows a slower cold request.

Credentials and the endpoint are in `~/.config/laya/config.json`, mode `0600`.
Alternatively set `LAYA_ENDPOINT` and `LAYA_API_TOKEN` in the calling environment;
no config file is needed when both are set. Environment values override the file.
The helper reads credentials itself. Do not read that file into chat, copy the token into
a command, or place credentials in a project. `LAYA_API_TOKEN`, if exported in
the calling process, overrides the stored token. Authentication is Bearer.

For a connection smoke test, use the bundled synthetic fixture:

```bash
python3 ~/.agents/skills/laya-decisions/scripts/predict.py \
  --input ~/.agents/skills/laya-decisions/assets/smoke-request.json
```

For skill selection, first make a small shortlist from actual installed skill
descriptions, include a no-match option, then evaluate the result against the
task before loading the selected skill. Keep state concise: upstream checkpoints
have short context limits and may truncate long inputs. Do not send full repos,
credentials, or unrelated private context to obtain a routing decision.

Treat answers and confidence as advisory. Use ordinary code for exact rules;
keep complex reasoning, permissions and verification with the host agent.
Do not add a network call to every step. A successful request does not establish
accuracy or a speed improvement; measure representative tasks before relying
on repeated routing. If the service fails, report the failure and continue
host reasoning when appropriate without presenting it as a Laya result.
