"""Tests for the PNG XMP handler."""

from __future__ import annotations

import binascii
import zlib

from swarmauri_xmp_png import PNGXMP


def _chunk(ctype: bytes, payload: bytes) -> bytes:
    length = len(payload).to_bytes(4, "big")
    crc = (binascii.crc32(ctype + payload) & 0xFFFFFFFF).to_bytes(4, "big")
    return length + ctype + payload + crc


def _minimal_png() -> bytes:
    ihdr = (
        b"\x00\x00\x00\x01"  # width
        + b"\x00\x00\x00\x01"  # height
        + b"\x08"  # bit depth
        + b"\x02"  # color type RGB
        + b"\x00"  # compression
        + b"\x00"  # filter
        + b"\x00"  # interlace
    )
    idat = zlib.compress(b"\x00\x00\x00\x00")
    png = (
        PNGXMP.PNG_SIG
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )
    return png


def test_png_round_trip() -> None:
    handler = PNGXMP()
    source = _minimal_png()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    written = handler.write_xmp(source, xmp)
    assert handler.read_xmp(written) == xmp

    stripped = handler.remove_xmp(written)
    assert stripped == source
    assert handler.read_xmp(stripped) is None
