"""Peagen gateway exceptions."""
from __future__ import annotations


class PeagenError(Exception):
    """Base exception for Peagen-related errors."""


class PeagenHashMismatchError(PeagenError):
    """Raised when a supplied hash does not match computed value."""
