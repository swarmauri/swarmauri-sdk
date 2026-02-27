# Session Architecture

Tigrbl session support is organized across core layers:

- `_spec/session_spec.py`: `SessionSpec` policy model plus helpers (`session_spec`, `tx_*`, `readonly`, `wrap_sessionmaker`).
- `_base/_session_abc.py`: `SessionABC` contract expected by runtime and adapters.
- `_base/_session_base.py`: `TigrblSessionBase` guardrails and transaction behavior.
- `_concrete/_session.py`: `DefaultSession` delegating wrapper for provider-native sessions.
- `decorators/session.py`: `session_ctx` and `read_only_session` decorators for app/router/model/op policy scopes.

This design is backend-agnostic and does not depend on specific database drivers.
