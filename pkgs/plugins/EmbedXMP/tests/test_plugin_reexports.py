"""Tests for the EmbedXMP plugin exports."""

from __future__ import annotations

import binascii
import zlib

import EmbedXMP as plugin
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


def test_plugin_exports_expected_symbols() -> None:
    for name in [
        "EmbedXMP",
        "embed",
        "read",
        "remove",
        "embed_file",
        "read_file_xmp",
        "remove_file_xmp",
    ]:
        assert hasattr(plugin, name)
    assert plugin.EmbedXMP is EmbedXMP


def test_plugin_helpers_respect_custom_default() -> None:
    original = plugin._default_embed
    plugin._default_embed = EmbedXMP(handlers=[PNGXMP], eager_import=False)
    data = _minimal_png()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"
    try:
        written = plugin.embed(data, xmp, path="example.png")
        assert plugin.read(written, path="example.png") == xmp
        assert plugin.read(plugin.remove(written, path="example.png")) is None
    finally:
        plugin._default_embed = original
