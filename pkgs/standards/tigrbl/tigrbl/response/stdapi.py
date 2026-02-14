"""StdAPI response primitives."""

from __future__ import annotations

import json as json_module
import mimetypes
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any, AsyncIterator, Iterable, Mapping


class Headers(MutableMapping[str, str]):
    """Case-insensitive header mapping for response objects."""

    def __init__(
        self, values: Iterable[tuple[str, str]] | Mapping[str, str] | None = None
    ):
        self._data: dict[str, tuple[str, str]] = {}
        if values is None:
            return
        items = values.items() if hasattr(values, "items") else values
        for key, value in items:
            self._data[key.lower()] = (key.lower(), value)

    def __getitem__(self, key: str) -> str:
        return self._data[key.lower()][1]

    def __setitem__(self, key: str, value: str) -> None:
        self._data[key.lower()] = (key.lower(), value)

    def __delitem__(self, key: str) -> None:
        del self._data[key.lower()]

    def __iter__(self):
        for original, _ in self._data.values():
            yield original

    def __len__(self) -> int:
        return len(self._data)

    def items(self):
        return ((k, v) for k, v in self._data.values())

    def as_list(self) -> list[tuple[str, str]]:
        return [(k, v) for k, v in self._data.values()]


@dataclass
class Response:
    status_code: int = 200
    headers: list[tuple[str, str]] = field(default_factory=list)
    body: bytes = b""
    media_type: str | None = None
    _headers: Headers = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._headers = Headers(self.headers)

    @staticmethod
    def _status_text(code: int) -> str:
        return {
            200: "OK",
            201: "Created",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
        }.get(code, "OK")

    def status_line(self) -> str:
        return f"{self.status_code} {self._status_text(self.status_code)}"

    @property
    def raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [
            (k.encode("latin-1"), v.encode("latin-1")) for k, v in self._headers.items()
        ]

    @property
    def headers_map(self) -> Headers:
        return self._headers

    @property
    def body_text(self) -> str:
        return self.body.decode("utf-8")

    def json_body(self) -> Any:
        if not self.body:
            return None
        return json_module.loads(self.body.decode("utf-8"))

    @property
    def cookies(self) -> dict[str, str]:
        cookie = SimpleCookie()
        for name, value in self._headers.items():
            if name == "set-cookie":
                cookie.load(value)
        return {name: morsel.value for name, morsel in cookie.items()}

    def set_cookie(self, key: str, value: str, *, path: str = "/") -> None:
        cookie = SimpleCookie()
        cookie[key] = value
        cookie[key]["path"] = path
        self._headers["set-cookie"] = cookie.output(header="").strip()
        self.headers = self._headers.as_list()

    @classmethod
    def json(
        cls,
        data: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = json_module.dumps(
            data, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        hdrs = [("content-type", "application/json; charset=utf-8")]
        for k, v in (headers or {}).items():
            hdrs.append((k.lower(), v))
        return cls(
            status_code=status_code,
            headers=hdrs,
            body=payload,
            media_type="application/json",
        )

    @classmethod
    def html(
        cls,
        html: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = html.encode("utf-8")
        hdrs = [("content-type", "text/html; charset=utf-8")]
        for k, v in (headers or {}).items():
            hdrs.append((k.lower(), v))
        return cls(
            status_code=status_code,
            headers=hdrs,
            body=payload,
            media_type="text/html",
        )

    @classmethod
    def text(
        cls,
        text: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = text.encode("utf-8")
        hdrs = [("content-type", "text/plain; charset=utf-8")]
        for k, v in (headers or {}).items():
            hdrs.append((k.lower(), v))
        return cls(
            status_code=status_code,
            headers=hdrs,
            body=payload,
            media_type="text/plain",
        )


class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200) -> None:
        payload = json_module.dumps(
            content, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "application/json; charset=utf-8")],
            body=payload,
            media_type="application/json",
        )


class HTMLResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/html; charset=utf-8")],
            body=content.encode("utf-8"),
            media_type="text/html",
        )


class PlainTextResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/plain; charset=utf-8")],
            body=content.encode("utf-8"),
            media_type="text/plain",
        )


class StreamingResponse(Response):
    def __init__(
        self,
        content: Iterable[bytes] | bytes,
        status_code: int = 200,
        media_type: str = "application/octet-stream",
    ) -> None:
        chunks = [content] if isinstance(content, bytes) else list(content)
        super().__init__(
            status_code=status_code,
            headers=[("content-type", media_type)],
            body=b"".join(chunks),
            media_type=media_type,
        )
        self._chunks = [bytes(chunk) for chunk in chunks]

    @property
    def body_iterator(self) -> AsyncIterator[bytes]:
        async def _iter() -> AsyncIterator[bytes]:
            for chunk in self._chunks:
                yield chunk

        return _iter()


class FileResponse(Response):
    def __init__(self, path: str, media_type: str | None = None) -> None:
        payload = Path(path).read_bytes()
        content_type = (
            media_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        super().__init__(
            status_code=200,
            headers=[("content-type", content_type)],
            body=payload,
            media_type=content_type,
        )
        self.path = str(path)


class RedirectResponse(Response):
    def __init__(self, url: str, status_code: int = 307) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("location", url)],
            body=b"",
            media_type=None,
        )
        self.url = url


__all__ = [
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "StreamingResponse",
    "FileResponse",
    "RedirectResponse",
]
