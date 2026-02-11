"""Compatibility re-exports for API dependency wrappers."""

from __future__ import annotations

from ..security.dependencies import Dependency, Depends, Security
from ..security import HTTPAuthorizationCredentials as HTTPAuthorizationCredentials
from ..security import HTTPBearer as HTTPBearer

_Dependency = Dependency

__all__ = [
    "HTTPAuthorizationCredentials",
    "HTTPBearer",
    "Dependency",
    "_Dependency",
    "Depends",
    "Security",
]
