"""Tests for the TIFF XMP handler scaffold."""

from __future__ import annotations

import pytest

from swarmauri_xmp_tiff import TIFFXMP


def _minimal_tiff() -> bytes:
    return b"II*\x00" + b"\x00" * 8


def test_tiff_methods_raise_not_implemented() -> None:
    handler = TIFFXMP()
    data = _minimal_tiff()
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    with pytest.raises(NotImplementedError):
        handler.read_xmp(data)
    with pytest.raises(NotImplementedError):
        handler.write_xmp(data, xmp)
    with pytest.raises(NotImplementedError):
        handler.remove_xmp(data)
