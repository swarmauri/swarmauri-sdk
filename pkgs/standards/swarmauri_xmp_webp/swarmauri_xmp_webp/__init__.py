"""WebP XMP handler implementation."""

from __future__ import annotations

from typing import ClassVar, Iterator, Tuple

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class WebPXMP(EmbedXmpBase):
    """Embed and extract XMP packets using WebP ``XMP `` chunks."""

    SIGNATURE: ClassVar[bytes] = b"RIFF"
    FORMAT: ClassVar[bytes] = b"WEBP"
    XMP_CHUNK: ClassVar[bytes] = b"XMP "

    def _validate(self, data: bytes) -> None:
        if len(data) < 12 or not data.startswith(self.SIGNATURE):
            raise ValueError("Not a WebP payload")
        if data[8:12] != self.FORMAT:
            raise ValueError("RIFF container is not WebP formatted")

    def _iter_chunks(self, data: bytes) -> Iterator[Tuple[int, bytes, int, int]]:
        self._validate(data)
        pos = 12
        end = len(data)
        while pos + 8 <= end:
            ctype = data[pos : pos + 4]
            size = int.from_bytes(data[pos + 4 : pos + 8], "little")
            data_start = pos + 8
            data_end = data_start + size
            if data_end > end:
                raise ValueError("Truncated WebP chunk")
            yield pos, ctype, data_start, size
            pos = data_end + (size & 1)
        if pos != end:
            # Allow a single padding byte
            if not (pos == end - 1 and data[-1] == 0):
                raise ValueError("Unexpected trailer in WebP payload")

    def supports(self, header: bytes, path: str) -> bool:
        return path.lower().endswith(".webp") or (
            header.startswith(self.SIGNATURE) and header[8:12] == self.FORMAT
        )

    def read_xmp(self, data: bytes) -> str | None:
        for _offset, ctype, data_off, data_len in self._iter_chunks(data):
            if ctype != self.XMP_CHUNK:
                continue
            payload = data[data_off : data_off + data_len]
            return payload.decode("utf-8", errors="ignore")
        return None

    def _chunk_bytes(self, ctype: bytes, payload: bytes) -> bytes:
        chunk = bytearray()
        chunk.extend(ctype)
        chunk.extend(len(payload).to_bytes(4, "little"))
        chunk.extend(payload)
        if len(payload) & 1:
            chunk.append(0)
        return bytes(chunk)

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        xmp_bytes = self._ensure_xml(xmp_xml)
        self._validate(data)
        chunks = []
        for _offset, ctype, data_off, data_len in self._iter_chunks(data):
            if ctype == self.XMP_CHUNK:
                continue
            payload = data[data_off : data_off + data_len]
            chunks.append(self._chunk_bytes(ctype, payload))
        chunks.append(self._chunk_bytes(self.XMP_CHUNK, xmp_bytes))
        body = b"".join(chunks)
        size = len(body) + len(self.FORMAT)
        return self.SIGNATURE + size.to_bytes(4, "little") + self.FORMAT + body

    def remove_xmp(self, data: bytes) -> bytes:
        self._validate(data)
        chunks = []
        for _offset, ctype, data_off, data_len in self._iter_chunks(data):
            if ctype == self.XMP_CHUNK:
                continue
            payload = data[data_off : data_off + data_len]
            chunks.append(self._chunk_bytes(ctype, payload))
        body = b"".join(chunks)
        size = len(body) + len(self.FORMAT)
        return self.SIGNATURE + size.to_bytes(4, "little") + self.FORMAT + body


__all__ = ["WebPXMP"]
