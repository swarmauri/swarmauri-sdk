from __future__ import annotations

from typing import Any, Callable, Optional

from .default import DefaultSession
from .spec import SessionSpec, SessionCfg


def session_spec(cfg: SessionCfg = None, /, **kw: Any) -> SessionSpec:
    """
    Build a SessionSpec from either a mapping/spec or kwargs.
    """
    if cfg is not None and kw:
        raise ValueError("Provide either a mapping/spec or kwargs, not both")
    return SessionSpec.from_any(cfg or kw) or SessionSpec()


# Isolation presets
def tx_read_committed(*, read_only: Optional[bool] = None) -> SessionSpec:
    return SessionSpec(isolation="read_committed", read_only=read_only)


def tx_repeatable_read(*, read_only: Optional[bool] = None) -> SessionSpec:
    return SessionSpec(isolation="repeatable_read", read_only=read_only)


def tx_serializable(*, read_only: Optional[bool] = None) -> SessionSpec:
    return SessionSpec(isolation="serializable", read_only=read_only)


def readonly() -> SessionSpec:
    return SessionSpec(read_only=True)


# Provider/sessionmaker wrapper
def wrap_sessionmaker(
    maker: Callable[[], Any], spec: SessionSpec
) -> Callable[[], DefaultSession]:
    """
    Wrap any provider's session factory to yield DefaultSession instances that
    enforce the Tigrbl Session ABC and policy.
    """

    def _mk() -> DefaultSession:
        underlying = maker()
        s = DefaultSession(underlying, spec)
        s.apply_spec(spec)
        return s

    return _mk
