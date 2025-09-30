"""Abstract base interface for XMP embedding handlers."""

from __future__ import annotations

import abc
from typing import Optional


class IEmbedXMP(abc.ABC):
    """Interface implemented by components that manage embedded XMP packets."""

    @abc.abstractmethod
    def supports(self, header: bytes, path: str) -> bool:
        """Return ``True`` when the handler can operate on the supplied payload."""

    @abc.abstractmethod
    def read_xmp(self, data: bytes) -> Optional[str]:
        """Extract an XMP packet from ``data`` if present."""

    @abc.abstractmethod
    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        """Return a copy of ``data`` with ``xmp_xml`` embedded."""

    @abc.abstractmethod
    def remove_xmp(self, data: bytes) -> bytes:
        """Return ``data`` with any embedded XMP removed."""
