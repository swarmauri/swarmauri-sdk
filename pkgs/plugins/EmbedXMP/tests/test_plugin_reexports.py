"""Tests for the EmbedXMP plugin re-exports."""

from __future__ import annotations

import binascii
import zlib

import EmbedXMP as plugin
import swarmauri_embed_xmp as standard
from swarmauri_embed_xmp import EmbedXMP
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


def test_plugin_symbols_match_standard() -> None:
    assert plugin.EmbedXMP is standard.EmbedXMP
    assert plugin.embed is standard.embed
    assert plugin.read is standard.read
    assert plugin.remove is standard.remove


def test_plugin_helpers_respect_custom_default() -> None:
    original = standard._default_embed
    standard._default_embed = EmbedXMP(handlers=[PNGXMP], eager_import=False)
    data = _minimal_png()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"
    try:
        written = plugin.embed(data, xmp, path="example.png")
        assert plugin.read(written, path="example.png") == xmp
        assert plugin.read(plugin.remove(written, path="example.png")) is None
    finally:
        standard._default_embed = original
