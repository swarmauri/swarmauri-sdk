"""Security dependency wrappers for stdapi."""

from __future__ import annotations

from typing import Any, Callable

from ..security import HTTPAuthorizationCredentials as HTTPAuthorizationCredentials
from ..security import HTTPBearer as HTTPBearer


class _Dependency:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency


def Depends(fn: Callable[..., Any]) -> _Dependency:
    return _Dependency(fn)


def Security(fn: Callable[..., Any]) -> _Dependency:
    return _Dependency(fn)


__all__ = [
    "HTTPAuthorizationCredentials",
    "HTTPBearer",
    "_Dependency",
    "Depends",
    "Security",
]
