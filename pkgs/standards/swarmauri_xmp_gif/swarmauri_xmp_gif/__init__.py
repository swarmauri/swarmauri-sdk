"""GIF Application Extension XMP handler."""

from __future__ import annotations

import io
from typing import ClassVar

from swarmauri_base import register_type
from swarmauri_base.xmp import EmbedXmpBase


@register_type(resource_type=EmbedXmpBase)
class GIFXMP(EmbedXmpBase):
    """Embed XMP packets using a GIF89a application extension."""

    SIG87: ClassVar[bytes] = b"GIF87a"
    SIG89: ClassVar[bytes] = b"GIF89a"
    APP_EXT: ClassVar[int] = 0xFF
    XMP_ID: ClassVar[bytes] = b"XMP Data"
    XMP_AUTH: ClassVar[bytes] = b"XMP"

    def supports(self, header: bytes, path: str) -> bool:
        return header.startswith(self.SIG89) or path.lower().endswith(".gif")

    def read_xmp(self, data: bytes) -> str | None:
        i = 0
        n = len(data)
        while i + 14 <= n:
            if data[i] == 0x21 and i + 1 < n and data[i + 1] == self.APP_EXT:
                if i + 2 >= n:
                    break
                block_len = data[i + 2]
                if block_len != 11:
                    i += 1
                    continue
                if i + 3 + 11 > n:
                    break
                app_id = data[i + 3 : i + 11]
                auth = data[i + 11 : i + 14]
                j = i + 14
                if app_id == self.XMP_ID and auth == self.XMP_AUTH:
                    buf = bytearray()
                    while j < n and data[j] != 0x00:
                        sz = data[j]
                        j += 1
                        if j + sz > n:
                            break
                        buf.extend(data[j : j + sz])
                        j += sz
                    try:
                        return bytes(buf).decode("utf-8")
                    except UnicodeDecodeError:
                        return None
                else:
                    while j < n and data[j] != 0x00:
                        sz = data[j]
                        j += 1 + sz
                    i = j + 1
                    continue
            i += 1
        return None

    def _app_ext(self, payload: bytes) -> bytes:
        out = bytearray(b"\x21\xff\x0b")
        out.extend(self.XMP_ID[:8])
        out.extend(self.XMP_AUTH[:3])
        i = 0
        while i < len(payload):
            chunk = payload[i : i + 255]
            i += len(chunk)
            out.append(len(chunk))
            out.extend(chunk)
        out.append(0x00)
        return bytes(out)

    def write_xmp(self, data: bytes, xmp_xml: str) -> bytes:
        if not (data.startswith(self.SIG89) or data.startswith(self.SIG87)):
            raise ValueError("Not a GIF payload")
        xmp_bytes = self._ensure_xml(xmp_xml)
        out = io.BytesIO()
        out.write(data[:13])
        packed = data[10]
        gct_flag = (packed & 0x80) != 0
        gct_size = 3 * (2 ** ((packed & 0x07) + 1)) if gct_flag else 0
        out.write(data[13 : 13 + gct_size])
        out.write(self._app_ext(xmp_bytes))
        i = 13 + gct_size
        n = len(data)
        while i < n:
            if (
                data[i] == 0x21
                and i + 1 < n
                and data[i + 1] == self.APP_EXT
                and i + 2 < n
                and data[i + 2] == 11
            ):
                app_id = data[i + 3 : i + 11]
                auth = data[i + 11 : i + 14]
                j = i + 14
                while j < n and data[j] != 0x00:
                    j += 1 + data[j]
                j += 1
                if app_id == self.XMP_ID and auth == self.XMP_AUTH:
                    i = j
                    continue
                out.write(data[i:j])
                i = j
                continue
            out.write(data[i : i + 1])
            i += 1
        return out.getvalue()

    def remove_xmp(self, data: bytes) -> bytes:
        if not (data.startswith(self.SIG89) or data.startswith(self.SIG87)):
            raise ValueError("Not a GIF payload")
        out = io.BytesIO()
        i = 0
        n = len(data)
        while i < n:
            if (
                data[i] == 0x21
                and i + 1 < n
                and data[i + 1] == self.APP_EXT
                and i + 2 < n
                and data[i + 2] == 11
            ):
                app_id = data[i + 3 : i + 11]
                auth = data[i + 11 : i + 14]
                j = i + 14
                while j < n and data[j] != 0x00:
                    j += 1 + data[j]
                j += 1
                if app_id == self.XMP_ID and auth == self.XMP_AUTH:
                    i = j
                    continue
                out.write(data[i:j])
                i = j
                continue
            out.write(data[i : i + 1])
            i += 1
        return out.getvalue()


__all__ = ["GIFXMP"]
