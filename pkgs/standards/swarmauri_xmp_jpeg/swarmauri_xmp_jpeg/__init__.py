"""JPEG APP1 XMP handler."""

from __future__ import annotations

import io
from typing import ClassVar, Iterator, Tuple

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class JPEGXMP(EmbedXmpBase):
    """Embed XMP packets inside JPEG APP1 segments."""

    SOI: ClassVar[bytes] = b"\xff\xd8"
    EOI: ClassVar[bytes] = b"\xff\xd9"
    SOS: ClassVar[int] = 0xDA
    APP1: ClassVar[int] = 0xE1
    XMP_HDR: ClassVar[bytes] = b"http://ns.adobe.com/xap/1.0/\x00"

    def supports(self, header: bytes, path: str) -> bool:
        return header.startswith(self.SOI) or path.lower().endswith((".jpg", ".jpeg"))

    def _iter_segments(self, data: bytes) -> Iterator[Tuple[int, int, int, int]]:
        if not data.startswith(self.SOI):
            raise ValueError("Not a JPEG payload")
        n = len(data)
        i = 2
        yield 0, 0xD8, 0, 0
        while i < n:
            if data[i] != 0xFF:
                return
            j = i
            while j < n and data[j] == 0xFF:
                j += 1
            if j >= n:
                return
            marker = data[j]
            i = j + 1
            if marker == self.SOS:
                if i + 2 > n:
                    raise ValueError("Truncated SOS segment")
                seglen = int.from_bytes(data[i : i + 2], "big")
                yield j - 1, marker, i, seglen - 2
                return
            if i + 2 > n:
                return
            seglen = int.from_bytes(data[i : i + 2], "big")
            if seglen < 2 or i + seglen > n:
                raise ValueError("Invalid JPEG segment length")
            yield j - 1, marker, i, seglen - 2
            i += seglen

    def read_xmp(self, data: bytes) -> str | None:
        for _m_off, marker, p_off, p_len in self._iter_segments(data):
            if marker != self.APP1:
                continue
            payload = data[p_off + 2 : p_off + 2 + p_len]
            if payload.startswith(self.XMP_HDR):
                return payload[len(self.XMP_HDR) :].decode("utf-8", errors="ignore")
        return None

    def _build_app1(self, xmp_utf8: bytes) -> bytes:
        payload = self.XMP_HDR + xmp_utf8
        seglen = 2 + len(payload)
        return b"\xff" + bytes([self.APP1]) + seglen.to_bytes(2, "big") + payload

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        xmp_bytes = self._ensure_xml(xmp_xml)
        if not data.startswith(self.SOI):
            raise ValueError("Not a JPEG payload")
        out = io.BytesIO()
        out.write(self.SOI)
        inserted = False
        for _m_off, marker, p_off, p_len in self._iter_segments(data):
            if marker == 0xD8:
                continue
            if not inserted:
                out.write(self._build_app1(xmp_bytes))
                inserted = True
            if marker == self.APP1:
                payload = data[p_off + 2 : p_off + 2 + p_len]
                if payload.startswith(self.XMP_HDR):
                    continue
            out.write(b"\xff" + bytes([marker]) + data[p_off : p_off + 2 + p_len])
        if not inserted:
            out.write(self._build_app1(xmp_bytes))
            out.write(data[2:])
        return out.getvalue()

    def remove_xmp(self, data: bytes) -> bytes:
        if not data.startswith(self.SOI):
            raise ValueError("Not a JPEG payload")
        out = io.BytesIO()
        out.write(self.SOI)
        for _m_off, marker, p_off, p_len in self._iter_segments(data):
            if marker == 0xD8:
                continue
            if marker == self.APP1:
                payload = data[p_off + 2 : p_off + 2 + p_len]
                if payload.startswith(self.XMP_HDR):
                    continue
            out.write(b"\xff" + bytes([marker]) + data[p_off : p_off + 2 + p_len])
        return out.getvalue()


__all__ = ["JPEGXMP"]
