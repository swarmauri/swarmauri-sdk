"""SVG metadata XMP handler."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class SVGXMP(EmbedXmpBase):
    """Embed XMP metadata into SVG `<metadata>` elements."""

    def supports(self, header: bytes, path: str) -> bool:
        return path.lower().endswith(".svg") or header.strip().startswith(b"<")

    def _insert_metadata(self, svg_text: str, xmp_xml: str) -> str:
        try:
            root = ET.fromstring(svg_text)
        except ET.ParseError:
            idx = svg_text.find("<svg")
            if idx == -1:
                raise
            end = svg_text.find(">", idx)
            return (
                svg_text[: end + 1]
                + "\n<metadata>\n"
                + xmp_xml
                + "\n</metadata>\n"
                + svg_text[end + 1 :]
            )
        for child in list(root):
            if child.tag.endswith("metadata"):
                root.remove(child)
        md = ET.Element("metadata")
        md.text = xmp_xml
        root.insert(0, md)
        return ET.tostring(root, encoding="unicode")

    def read_xmp(self, data: bytes) -> str | None:
        text = data.decode("utf-8", errors="ignore")
        start = text.find("<metadata")
        if start == -1:
            return None
        start_end = text.find(">", start)
        if start_end == -1:
            return None
        end = text.find("</metadata>", start_end)
        if end == -1:
            return None
        content = text[start_end + 1 : end].strip()
        return html.unescape(content)

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        text = data.decode("utf-8", errors="ignore")
        result = self._insert_metadata(text, xmp_xml)
        return result.encode("utf-8")

    def remove_xmp(self, data: bytes) -> bytes:
        text = data.decode("utf-8", errors="ignore")
        start = text.find("<metadata")
        if start == -1:
            return data
        start_end = text.find(">", start)
        end = text.find("</metadata>", start_end)
        if start_end == -1 or end == -1:
            return data
        return (text[:start] + text[end + 11 :]).encode("utf-8")


__all__ = ["SVGXMP"]
