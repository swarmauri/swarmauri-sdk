"""Plugin package that re-exports the standard EmbedXMP manager."""

from __future__ import annotations

from swarmauri_embed_xmp import (
    EmbedXMP,
    embed,
    embed_file,
    read,
    read_file_xmp,
    remove,
    remove_file_xmp,
)

__all__ = [
    "EmbedXMP",
    "embed",
    "read",
    "remove",
    "embed_file",
    "read_file_xmp",
    "remove_file_xmp",
]
