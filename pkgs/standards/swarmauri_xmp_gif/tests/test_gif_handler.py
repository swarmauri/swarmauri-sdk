"""Tests for the GIF XMP handler."""

from __future__ import annotations

from swarmauri_xmp_gif import GIFXMP


def _minimal_gif() -> bytes:
    return (
        b"GIF89a"
        + b"\x01\x00\x01\x00"  # canvas size
        + b"\x00"  # packed fields (no GCT)
        + b"\x00"  # bg color index
        + b"\x00"  # pixel aspect ratio
        + b"\x3b"  # trailer
    )


def test_gif_round_trip() -> None:
    handler = GIFXMP()
    source = _minimal_gif()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    written = handler.write_xmp(source, xmp)
    assert handler.read_xmp(written) == xmp

    stripped = handler.remove_xmp(written)
    assert stripped == source
