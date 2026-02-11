"""Dependency wrappers for API/security injection semantics."""

from __future__ import annotations

from typing import Any, Callable


class Dependency:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency


def Depends(fn: Callable[..., Any]) -> Dependency:
    return Dependency(fn)


def Security(fn: Callable[..., Any]) -> Dependency:
    return Dependency(fn)


__all__ = ["Dependency", "Depends", "Security"]
