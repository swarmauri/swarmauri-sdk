"""Tests for the generic EmbedXMP manager."""

from __future__ import annotations

import binascii
import zlib

import EmbedXMP as manager
from EmbedXMP import EmbedXMP
from swarmauri_xmp_png import PNGXMP


def _chunk(ctype: bytes, payload: bytes) -> bytes:
    length = len(payload).to_bytes(4, "big")
    crc = (binascii.crc32(ctype + payload) & 0xFFFFFFFF).to_bytes(4, "big")
    return length + ctype + payload + crc


def _minimal_png() -> bytes:
    ihdr = (
        b"\x00\x00\x00\x01"
        + b"\x00\x00\x00\x01"
        + b"\x08"
        + b"\x02"
        + b"\x00"
        + b"\x00"
        + b"\x00"
    )
    idat = zlib.compress(b"\x00\x00\x00\x00")
    return (
        PNGXMP.PNG_SIG
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


def test_embedxmp_delegates_to_handlers() -> None:
    manager = EmbedXMP(handlers=[PNGXMP], eager_import=False)
    data = _minimal_png()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    written = manager.embed(data, xmp, path="example.png")
    assert manager.read(written, path="example.png") == xmp
    assert manager.remove(written, path="example.png").startswith(PNGXMP.PNG_SIG)


def test_module_helpers_use_cached_instance() -> None:
    original = manager._default_embed
    manager._default_embed = EmbedXMP(handlers=[PNGXMP], eager_import=False)
    data = _minimal_png()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"
    try:
        written = manager.embed(data, xmp, path="example.png")
        assert manager.read(written, path="example.png") == xmp
        assert manager.read(manager.remove(written, path="example.png")) is None
    finally:
        manager._default_embed = original
