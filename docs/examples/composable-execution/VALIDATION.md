# Focused validation

Validated on Windows with CPython 3.12.13, using the matching editable
workspace packages in an isolated worktree.

| Check | Result |
| --- | --- |
| Nine new package suites, run independently with uv | 29 passed |
| Core execution/authorization contract tests | 10 passed |
| Existing component, token and checkpoint base checks | 4 passed |
| Agent runner suite including its new driver | 6 passed |
| State-driven unit suite including restart/join/split/callable checks | 159 passed, 1 skipped |
| Facade interface/citizenship suites including new components | 25 passed |
| Existing round-robin assignment suite | 12 passed |
| Total focused tests | 245 passed, 1 skipped |
| Ruff format/check on changed Python files | Passed |
| Ruff check with CI's shared configuration | Passed |
| Package metadata regression check against PR baseline | Passed |
| Nine new wheel builds using Poetry Core | Passed |
| Document assistant command | Completed with verified document result |
| Delegated research command | Completed; recipient grant depths 2, 1, 0 |

The skipped test is the existing optional headless visualization check.
The focused environment uses uv --no-sync with installed workspace revisions;
it does not establish a full-monorepo dependency resolution or release gate.

Invocation tests use the existing HttpxClient against a real HTTPX ASGI
transport and the receiving application. This validates HTTP protocol mapping
in process; it does not establish deployed HTTPS interoperability.
JWTs are actually signed and verified with generated local RSA keys.
Model choices in CLI/tests use the explicitly named ScriptedDocumentModel.
Provider login-session tests use a provider test double. No live OAuth/OIDC
provider or live LLM calls were performed, and no packages were published.

Run scripts/verify_composable_execution.py from the prepared environment to
repeat the nine isolated suites. The composition README explains dependencies,
custom factor injection, login admission, HTTP hosting and crash recovery.
