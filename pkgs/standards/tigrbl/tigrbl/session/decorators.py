from __future__ import annotations

from typing import Any, Optional
from .spec import SessionSpec, SessionCfg


def _normalize(cfg: Optional[SessionCfg] = None, **kw: Any) -> SessionSpec:
    if cfg is not None and kw:
        raise ValueError("Pass either a mapping/spec or keyword args, not both")
    return SessionSpec.from_any(cfg or kw) or SessionSpec()


def session_ctx(cfg: Optional[SessionCfg] = None, /, **kw: Any):
    """
    Attach a SessionSpec to an App, API, Model/Table, or op handler.

    Precedence is evaluated by the resolver using:
        op > model > api > app
    (Resolver is part of the runtime/engine layer and is independent of this decorator.)
    """
    spec = _normalize(cfg, **kw)

    def _apply(obj: Any) -> Any:
        setattr(obj, "__tigrbl_session_ctx__", spec)
        return obj

    return _apply


def read_only_session(obj: Any = None, /, *, isolation: Optional[str] = None):
    """
    Convenience decorator for read-only sessions.
    """

    def _wrap(o: Any) -> Any:
        setattr(
            o,
            "__tigrbl_session_ctx__",
            SessionSpec(read_only=True, isolation=isolation),
        )
        return o

    return _wrap(obj) if obj is not None else _wrap
