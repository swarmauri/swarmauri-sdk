"""Tests for the SVG XMP handler."""

from __future__ import annotations

from swarmauri_xmp_svg import SVGXMP


def test_svg_round_trip() -> None:
    handler = SVGXMP()
    svg = "<svg xmlns='http://www.w3.org/2000/svg'><rect width='1' height='1'/></svg>"
    xmp = "<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF/></x:xmpmeta>"

    written = handler.write_xmp(svg.encode("utf-8"), xmp)
    read_back = handler.read_xmp(written)
    assert read_back is not None
    assert xmp in read_back or read_back == xmp

    stripped = handler.remove_xmp(written)
    assert xmp not in stripped.decode("utf-8")
