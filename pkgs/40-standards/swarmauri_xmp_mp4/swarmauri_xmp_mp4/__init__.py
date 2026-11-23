"""ISO-BMFF XMP handler scaffold."""

from __future__ import annotations

from typing import ClassVar, Tuple

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class MP4XMP(EmbedXmpBase):
    """Placeholder handler for ISO-BMFF containers."""

    SUPPORTED_EXTENSIONS: ClassVar[Tuple[str, ...]] = (
        ".mp4",
        ".mov",
        ".heic",
        ".heif",
        ".avif",
    )

    def supports(self, header: bytes, path: str) -> bool:
        lower = path.lower()
        return lower.endswith(self.SUPPORTED_EXTENSIONS)

    def read_xmp(self, data: bytes) -> str | None:
        raise NotImplementedError("ISO-BMFF XMP read not implemented yet")

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        raise NotImplementedError("ISO-BMFF XMP write not implemented yet")

    def remove_xmp(self, data: bytes) -> bytes:
        raise NotImplementedError("ISO-BMFF XMP remove not implemented yet")


__all__ = ["MP4XMP"]
