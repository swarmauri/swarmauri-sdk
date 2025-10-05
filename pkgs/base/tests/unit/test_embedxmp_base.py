"""Unit tests for the EmbedXmpBase helper methods."""

from __future__ import annotations

import pytest

from swarmauri_base.xmp import EmbedXmpBase


class _ConcreteEmbed(EmbedXmpBase):
    def supports(
        self, header: bytes, path: str
    ) -> bool:  # pragma: no cover - behavior tested elsewhere
        return True

    def read_xmp(self, data: bytes) -> str | None:  # pragma: no cover - placeholder
        return None

    def write_xmp(
        self, data: bytes, xmp_xml: str
    ) -> bytes:  # pragma: no cover - placeholder
        return data

    def remove_xmp(self, data: bytes) -> bytes:  # pragma: no cover - placeholder
        return data


def test_ensure_xml_accepts_rdf_packets() -> None:
    handler = _ConcreteEmbed()
    xml = "<x:xmpmeta><rdf:RDF/></x:xmpmeta>"
    assert handler._ensure_xml(xml) == xml.encode("utf-8")


def test_ensure_xml_rejects_non_rdf() -> None:
    handler = _ConcreteEmbed()
    with pytest.raises(ValueError):
        handler._ensure_xml("<metadata></metadata>")


def test_resource_defaults_to_embedxmp() -> None:
    handler = _ConcreteEmbed()
    assert handler.resource == "EmbedXMP"
