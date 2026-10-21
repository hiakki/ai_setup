# Output handling

RTK's OSS edition is installed as an explicit CLI; no `rtk init`, shell/agent
hooks, proxy daemon or proprietary engine is enabled. Start with
`rtk --help`, then a read-only command such as `rtk git status` in the authorized
repo. Check its exit code. For debugging, rerun the original command directly
and preserve raw stderr/stdout; filtered output can omit decisive evidence.
Never use compressed output as proof that no test failed or no match exists.

Use existing Context Mode for large repeated local-document/log queries, and
direct reads for small material. Both are local output tools, not new canonical
memory systems. Report measured output reduction separately from model-token,
latency or bill savings; RTK's estimates do not establish the latter.

Source: [RTK provider](https://github.com/rtk-ai/rtk).
