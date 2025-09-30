"""TIFF/DNG XMP handler scaffold."""

from __future__ import annotations

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class TIFFXMP(EmbedXmpBase):
    """Placeholder for TIFF and DNG XMP support."""

    def supports(self, header: bytes, path: str) -> bool:
        return path.lower().endswith((".tif", ".tiff")) or header.startswith(
            (b"II*\x00", b"MM\x00*")
        )

    def read_xmp(self, data: bytes) -> str | None:
        raise NotImplementedError("TIFF/DNG XMP read not implemented yet")

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        raise NotImplementedError("TIFF/DNG XMP write not implemented yet")

    def remove_xmp(self, data: bytes) -> bytes:
        raise NotImplementedError("TIFF/DNG XMP remove not implemented yet")


__all__ = ["TIFFXMP"]
