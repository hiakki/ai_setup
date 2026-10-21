# Structural and API checks

## ast-grep

Use `ast-grep run --lang typescript --pattern 'console.log($$$ARGS)' src` for a
syntax-aware read-only search after graph discovery where appropriate. Quote
patterns literally (PowerShell single quotes also prevent `$` expansion).
Inspect matches before any rewrite. Keep maintained rules and their positive
and negative fixture tests with the app; run `ast-grep test` for rule regressions.
Never run a repository-wide rewrite merely to follow a stylistic preference.
See [official guide](https://ast-grep.github.io/guide/introduction.html).

## Schemathesis

First read `schemathesis run --help`; use the app-owned OpenAPI/GraphQL contract.
Confirm the exact target, allowed operations, disposable data, request budget,
authentication and cleanup. Prefer an isolated test instance. Generated/stateful
requests may create, update or delete data; API testing is not implicitly safe.

Example for an explicitly authorized loopback fixture:

```
schemathesis run http://127.0.0.1:PORT/openapi.json --max-examples 10 --workers 1
```

Use provider-supported filters for approved operations. Do not leak tokens via
command arguments or logs; follow the app's credential injection and sanitize
reports. Preserve failing examples and reproduce them through the application's
real client/SDK. A schema pass is not proof of financial settlement, permission
correctness, production readiness or full business-workflow correctness.

See [official documentation](https://schemathesis.readthedocs.io/en/stable/).
