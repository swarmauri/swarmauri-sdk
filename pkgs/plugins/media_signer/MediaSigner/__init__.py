"""Swarmauri signing facade plugin that re-exports the :class:`MediaSigner`."""

from __future__ import annotations

from .signer import MediaSigner

__all__ = ["MediaSigner"]
