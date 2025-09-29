"""Unit tests for the IEmbedXMP interface."""

from __future__ import annotations

import pytest

from swarmauri_core.xmp import IEmbedXMP


class _MinimalHandler(IEmbedXMP):
    def supports(
        self, header: bytes, path: str
    ) -> bool:  # pragma: no cover - interface contract
        return True

    def read_xmp(
        self, data: bytes
    ) -> str | None:  # pragma: no cover - interface contract
        return "<rdf:RDF/>"

    def write_xmp(
        self, data: bytes, xmp_xml: str
    ) -> bytes:  # pragma: no cover - interface contract
        return data

    def remove_xmp(self, data: bytes) -> bytes:  # pragma: no cover - interface contract
        return data


def test_interface_requires_all_methods() -> None:
    class _Incomplete(IEmbedXMP):  # pragma: no cover - exercised via instantiation
        def supports(self, header: bytes, path: str) -> bool:
            return False

        def read_xmp(self, data: bytes) -> str | None:  # type: ignore[override]
            return None

    with pytest.raises(TypeError):
        _Incomplete()


def test_interface_can_be_subclassed() -> None:
    handler = _MinimalHandler()
    assert handler.supports(b"", "example"), "Expected subclass to be instantiable"
    assert handler.read_xmp(b"") == "<rdf:RDF/>"
    assert handler.write_xmp(b"data", "<rdf:RDF/>") == b"data"
    assert handler.remove_xmp(b"payload") == b"payload"
