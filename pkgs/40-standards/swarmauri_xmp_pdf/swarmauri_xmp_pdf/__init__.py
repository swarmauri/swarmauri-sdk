"""PDF XMP handler scaffold."""

from __future__ import annotations

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class PDFXMP(EmbedXmpBase):
    """Placeholder handler for PDF metadata streams."""

    def supports(self, header: bytes, path: str) -> bool:
        return path.lower().endswith(".pdf") or header.startswith(b"%PDF-")

    def read_xmp(self, data: bytes) -> str | None:
        raise NotImplementedError("PDF XMP read not implemented yet")

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        raise NotImplementedError("PDF XMP write not implemented yet")

    def remove_xmp(self, data: bytes) -> bytes:
        raise NotImplementedError("PDF XMP remove not implemented yet")


__all__ = ["PDFXMP"]
