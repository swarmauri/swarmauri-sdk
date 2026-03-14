"""Decorators for concrete Tigrbl model configuration."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

_T = TypeVar("_T", bound=type)


def allow_anon(*verbs: str):
    """Attach anonymous-operation metadata to a table class.

    Examples
    --------
    ``@allow_anon("list", "read")``
    """

    normalized = {verb.strip() for verb in verbs if verb and verb.strip()}

    def _decorate(cls: _T) -> _T:
        existing = getattr(cls, "__tigrbl_allow_anon__", set())
        if callable(existing):
            existing_value = existing()
        else:
            existing_value = existing

        merged = set(_as_iterable(existing_value)) | normalized
        setattr(cls, "__tigrbl_allow_anon__", merged)
        return cls

    return _decorate


def _as_iterable(value) -> Iterable[str]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return value
    return (str(value),)


__all__ = ["allow_anon"]
