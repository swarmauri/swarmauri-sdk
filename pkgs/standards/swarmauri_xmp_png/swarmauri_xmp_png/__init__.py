"""PNG XMP handler registered with Swarmauri's DynamicBase registry."""

from __future__ import annotations

import binascii
import io
from typing import ClassVar, Iterator, Tuple

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class PNGXMP(EmbedXmpBase):
    """Embed and extract XMP packets using PNG iTXt chunks."""

    PNG_SIG: ClassVar[bytes] = b"\x89PNG\r\n\x1a\n"
    KW: ClassVar[bytes] = b"XML:com.adobe.xmp"
    CHUNK_iTXt: ClassVar[bytes] = b"iTXt"

    def supports(self, header: bytes, path: str) -> bool:
        return header.startswith(self.PNG_SIG) or path.lower().endswith(".png")

    def _iter_chunks(self, data: bytes) -> Iterator[Tuple[int, bytes, int, int]]:
        if not data.startswith(self.PNG_SIG):
            raise ValueError("Not a PNG payload")
        i = len(self.PNG_SIG)
        n = len(data)
        while i + 8 <= n:
            length = int.from_bytes(data[i : i + 4], "big")
            ctype = data[i + 4 : i + 8]
            data_off = i + 8
            data_len = length
            crc_off = data_off + data_len
            if crc_off + 4 > n:
                raise ValueError("Truncated PNG chunk")
            yield i, ctype, data_off, data_len
            i = crc_off + 4

    def read_xmp(self, data: bytes) -> str | None:
        last: str | None = None
        for _off, ctype, d_off, d_len in self._iter_chunks(data):
            if ctype != self.CHUNK_iTXt:
                continue
            chunk = data[d_off : d_off + d_len]
            if b"\x00" not in chunk:
                continue
            keyword, rest = chunk.split(b"\x00", 1)
            if keyword != self.KW or len(rest) < 2:
                continue
            comp_flag = rest[0]
            if comp_flag:
                continue
            if len(rest) < 4:
                continue
            p = 2
            try:
                z1 = rest.index(b"\x00", p)
                p = z1 + 1
                z2 = rest.index(b"\x00", p)
                p = z2 + 1
            except ValueError:
                continue
            payload = rest[p:]
            try:
                last = payload.decode("utf-8")
            except UnicodeDecodeError:
                continue
        return last

    def _crc(self, ctype: bytes, payload: bytes) -> bytes:
        return (binascii.crc32(ctype + payload) & 0xFFFFFFFF).to_bytes(4, "big")

    def _build_itxt(self, text_utf8: bytes) -> bytes:
        payload = (
            self.KW
            + b"\x00"  # keyword terminator
            + b"\x00"  # compression flag
            + b"\x00"  # compression method
            + b"\x00"  # language tag
            + b"\x00"  # translated keyword
            + text_utf8
        )
        length = len(payload).to_bytes(4, "big")
        return length + self.CHUNK_iTXt + payload + self._crc(self.CHUNK_iTXt, payload)

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        xmp_bytes = self._ensure_xml(xmp_xml)
        out = io.BytesIO()
        out.write(self.PNG_SIG)
        for off, ctype, d_off, d_len in self._iter_chunks(data):
            if ctype == b"IEND":
                out.write(self._build_itxt(xmp_bytes))
            chunk = data[off : d_off + d_len + 4]
            if ctype == self.CHUNK_iTXt:
                payload = data[d_off : d_off + d_len]
                keyword = payload.split(b"\x00", 1)[0] if b"\x00" in payload else b""
                if keyword == self.KW:
                    continue
            out.write(chunk)
        return out.getvalue()

    def remove_xmp(self, data: bytes) -> bytes:
        out = io.BytesIO()
        out.write(self.PNG_SIG)
        for off, ctype, d_off, d_len in self._iter_chunks(data):
            if ctype == self.CHUNK_iTXt:
                payload = data[d_off : d_off + d_len]
                keyword = payload.split(b"\x00", 1)[0] if b"\x00" in payload else b""
                if keyword == self.KW:
                    continue
            out.write(data[off : d_off + d_len + 4])
        return out.getvalue()


__all__ = ["PNGXMP"]
