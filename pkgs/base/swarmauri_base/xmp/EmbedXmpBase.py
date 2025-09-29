"""Base implementation for XMP embedding handlers."""

from __future__ import annotations

import abc
from typing import ClassVar, Literal, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.xmp import IEmbedXMP


@ComponentBase.register_model()
class EmbedXmpBase(IEmbedXMP, ComponentBase):
    """Abstract component base class for XMP embedding handlers."""

    _type: ClassVar[str] = "EmbedXmpBase"
    type: Literal["EmbedXmpBase"] = "EmbedXmpBase"
    resource: Optional[str] = Field(default="EmbedXMP", frozen=True)

    @abc.abstractmethod
    def supports(self, header: bytes, path: str) -> bool:
        """Return ``True`` when the handler can operate on ``path``."""

    @abc.abstractmethod
    def read_xmp(self, data: bytes) -> Optional[str]:
        """Extract any embedded XMP packet from ``data``."""

    @abc.abstractmethod
    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        """Return ``data`` with ``xmp_xml`` embedded."""

    @abc.abstractmethod
    def remove_xmp(self, data: bytes) -> bytes:
        """Return ``data`` with XMP payloads removed."""

    def _ensure_xml(self, xmp_xml: str) -> bytes:
        """Validate that ``xmp_xml`` appears to be an RDF/XML packet."""

        if "<rdf:RDF" not in xmp_xml and "<x:xmpmeta" not in xmp_xml:
            raise ValueError(
                "XMP must be an RDF/XML packet containing <rdf:RDF> or <x:xmpmeta>."
            )
        return xmp_xml.encode("utf-8")
