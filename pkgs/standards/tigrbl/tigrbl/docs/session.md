# Session architecture

Tigrbl organizes session primitives across the canonical layers:

- `_spec.session_abc.SessionABC`: required transaction/session interface.
- `_spec.session_spec.SessionSpec`: per-session policy (isolation, read-only, timeouts, retries, etc.).
- `_base._session_base.TigrblSessionBase`: abstract base with guardrails (read-only enforcement, queued add()).
- `_concrete._session.DefaultSession`: delegating wrapper for native driver sessions.
- `decorators.session`: `session_ctx` / `read_only_session` helpers for app/router/model/op scopes.
- `shortcuts.session`: `session_spec` / `tx_*` / `readonly` and `wrap_sessionmaker` utilities.

This surface is backend-agnostic and does not import any database libraries.
