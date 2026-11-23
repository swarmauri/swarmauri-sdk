"""Tests for the JPEG XMP handler."""

from __future__ import annotations

from swarmauri_xmp_jpeg import JPEGXMP


def _minimal_jpeg() -> bytes:
    return (
        b"\xff\xd8"  # SOI
        + b"\xff\xe0\x00\x10JFIF\x00\x01\x02\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xd9"  # EOI
    )


def test_jpeg_round_trip() -> None:
    handler = JPEGXMP()
    source = _minimal_jpeg()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    written = handler.write_xmp(source, xmp)
    assert handler.read_xmp(written) == xmp

    stripped = handler.remove_xmp(written)
    assert stripped.startswith(b"\xff\xd8")
    assert handler.read_xmp(stripped) is None
