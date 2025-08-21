"""Signing interfaces and types."""

from .types import Signature

__all__ = ["ISigning", "Canon", "Envelope", "Signature"]


def __getattr__(name: str):
    if name in {"ISigning", "Canon", "Envelope"}:
        from .ISigning import ISigning, Canon, Envelope

        return {"ISigning": ISigning, "Canon": Canon, "Envelope": Envelope}[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")
