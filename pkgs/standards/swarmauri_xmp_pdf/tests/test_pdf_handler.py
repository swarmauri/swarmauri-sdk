"""Tests for the PDF XMP handler scaffold."""

from __future__ import annotations

import pytest

from swarmauri_xmp_pdf import PDFXMP


def test_pdf_methods_raise_not_implemented() -> None:
    handler = PDFXMP()
    data = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3"
    xmp = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"

    with pytest.raises(NotImplementedError):
        handler.read_xmp(data)
    with pytest.raises(NotImplementedError):
        handler.write_xmp(data, xmp)
    with pytest.raises(NotImplementedError):
        handler.remove_xmp(data)
