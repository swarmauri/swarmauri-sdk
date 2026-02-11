"""StdAPI response primitives."""

from __future__ import annotations

import json as json_module
import mimetypes
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class Response:
    status_code: int = 200
    headers: list[tuple[str, str]] = field(default_factory=list)
    body: bytes = b""

    @staticmethod
    def _status_text(code: int) -> str:
        return {
            200: "OK",
            201: "Created",
            204: "No Content",
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
        return cls(status_code=status_code, headers=hdrs, body=payload)

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
        return cls(status_code=status_code, headers=hdrs, body=payload)

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
        return cls(status_code=status_code, headers=hdrs, body=payload)


class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200) -> None:
        payload = json_module.dumps(
            content, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "application/json; charset=utf-8")],
            body=payload,
        )


class HTMLResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/html; charset=utf-8")],
            body=content.encode("utf-8"),
        )


class PlainTextResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/plain; charset=utf-8")],
            body=content.encode("utf-8"),
        )


class FileResponse(Response):
    def __init__(self, path: str, media_type: str | None = None) -> None:
        with open(path, "rb") as handle:
            payload = handle.read()
        content_type = (
            media_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        super().__init__(
            status_code=200,
            headers=[("content-type", content_type)],
            body=payload,
        )


__all__ = [
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "FileResponse",
]
