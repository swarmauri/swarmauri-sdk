"""Dependency wrappers for API/security injection semantics."""

from .._concrete.dependencies import Dependency, Depends, Security

__all__ = ["Depends", "Security", "Dependency"]
