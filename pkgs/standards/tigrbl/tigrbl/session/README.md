
# tigrbl.session

`tigrbl.session` provides the transaction-aware session contract and helpers for Tigrbl:

- `SessionABC`: required interface (native transactions).
- `SessionSpec`: per-session policy (isolation, read-only, timeouts, retries, etc.).
- `TigrblSessionBase`: abstract base with guardrails (read-only enforcement, queued add()).
- `DefaultSession`: delegating wrapper for native driver sessions.
- `session_ctx` / `read_only_session`: decorators to attach policy at app/api/model/op scopes.
- `session_spec` / `tx_*` / `readonly`: shortcuts to build policy objects.
- `wrap_sessionmaker`: helper to adapt provider session factories to Tigrbl sessions.

This module is backend-agnostic and does not import any database libraries.
