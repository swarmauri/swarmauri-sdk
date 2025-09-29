"""Tests for the WebP XMP handler."""

from __future__ import annotations

from swarmauri_xmp_webp import WebPXMP


def _minimal_webp() -> bytes:
    chunk_type = b"VP8 "
    payload = b""
    chunk = chunk_type + len(payload).to_bytes(4, "little") + payload
    body = chunk
    size = len(body) + 4
    return b"RIFF" + size.to_bytes(4, "little") + b"WEBP" + body


def test_webp_round_trip() -> None:
    handler = WebPXMP()
    source = _minimal_webp()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    written = handler.write_xmp(source, xmp)
    assert handler.read_xmp(written) == xmp

    stripped = handler.remove_xmp(written)
    assert handler.read_xmp(stripped) is None
