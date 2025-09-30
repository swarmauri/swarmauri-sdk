"""Tests for the MP4 XMP handler scaffold."""

from __future__ import annotations

import pytest

from swarmauri_xmp_mp4 import MP4XMP


def test_mp4_methods_raise_not_implemented() -> None:
    handler = MP4XMP()
    data = b"\x00\x00\x00\x18ftypmp42"
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    with pytest.raises(NotImplementedError):
        handler.read_xmp(data)
    with pytest.raises(NotImplementedError):
        handler.write_xmp(data, xmp)
    with pytest.raises(NotImplementedError):
        handler.remove_xmp(data)
