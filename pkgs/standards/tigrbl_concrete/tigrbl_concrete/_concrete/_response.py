from __future__ import annotations

from http.cookies import SimpleCookie
import base64
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Mapping

from tigrbl_base._base._response_base import ResponseBase, TemplateBase

from ._headers import HeaderCookies, Headers


class _JSONDualMethod:
    def __get__(self, obj: "Response" | None, owner: type["Response"]):
        if obj is None:

            def _factory(
                data: Any,
                status_code: int = 200,
                headers: Mapping[str, str] | None = None,
            ) -> "Response":
                return owner.from_json(data, status_code=status_code, headers=headers)

            return _factory

        return obj.json_body


class Template(TemplateBase):
    """Concrete template configuration used at runtime."""


class Response(ResponseBase):
    """Concrete response configuration used at runtime."""

    json = _JSONDualMethod()

    def __init__(
        self,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | list[tuple[str, str]] | None = None,
        body: bytes | None = None,
        content: bytes | None = None,
        media_type: str | None = None,
        kind: str = "auto",
        envelope: bool | None = None,
        template: TemplateBase | None = None,
        filename: str | None = None,
        download: bool | None = None,
        etag: str | None = None,
        cache_control: str | None = None,
        redirect_to: str | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            headers=headers,
            body=body,
            content=content,
            media_type=media_type,
            kind=kind,
            envelope=envelope,
            template=template,
            filename=filename,
            download=download,
            etag=etag,
            cache_control=cache_control,
            redirect_to=redirect_to,
        )
        self.headers = Headers(headers or {})

    @property
    def headers_map(self) -> Headers:
        return self.headers

    @property
    def cookies(self) -> HeaderCookies:
        parsed = SimpleCookie()
        for name, value in self.headers.items():
            if name == "set-cookie":
                parsed.load(value)
        return HeaderCookies({name: morsel.value for name, morsel in parsed.items()})

    @staticmethod
    def _status_text(code: int) -> str:
        return {
            200: "OK",
            201: "Created",
            205: "Reset Content",
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

    def set_cookie(
        self,
        key: str,
        value: str,
        *,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str | None = None,
        max_age: int | None = None,
        expires: str | None = None,
    ) -> None:
        cookie = SimpleCookie()
        cookie[key] = value
        morsel = cookie[key]
        morsel["path"] = path
        if domain is not None:
            morsel["domain"] = domain
        if secure:
            morsel["secure"] = True
        if httponly:
            morsel["httponly"] = True
        if samesite is not None:
            morsel["samesite"] = samesite
        if max_age is not None:
            morsel["max-age"] = str(max_age)
        if expires is not None:
            morsel["expires"] = expires
        self.headers["set-cookie"] = cookie.output(header="").strip()

    @classmethod
    def html(
        cls,
        html: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = html.encode("utf-8")
        hdrs = [("content-type", "text/html; charset=utf-8")]
        for key, value in (headers or {}).items():
            hdrs.append((key.lower(), value))
        return cls(
            status_code=status_code, headers=hdrs, body=payload, media_type="text/html"
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
        for key, value in (headers or {}).items():
            hdrs.append((key.lower(), value))
        return cls(
            status_code=status_code, headers=hdrs, body=payload, media_type="text/plain"
        )

    @classmethod
    def from_json(
        cls,
        data: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        import json as json_module

        payload = json_module.dumps(
            data, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        hdrs = [("content-type", "application/json; charset=utf-8")]
        for key, value in (headers or {}).items():
            hdrs.append((key.lower(), value))
        return cls(
            status_code=status_code,
            headers=hdrs,
            body=payload,
            media_type="application/json",
        )


def _json_default(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, Path):
        return str(value)
    return str(value)


try:
    import orjson as _orjson

    _ORJSON_OPTIONS = (
        getattr(_orjson, "OPT_NON_STR_KEYS", 0)
        | getattr(_orjson, "OPT_SERIALIZE_NUMPY", 0)
        | getattr(_orjson, "OPT_SERIALIZE_BYTES", 0)
    )

    def _dumps(obj: Any) -> bytes:
        try:
            return _orjson.dumps(
                obj,
                option=_ORJSON_OPTIONS,
                default=_json_default,
            )
        except TypeError:
            return json.dumps(
                obj,
                separators=(",", ":"),
                ensure_ascii=False,
                default=_json_default,
            ).encode("utf-8")
except Exception:  # pragma: no cover - fallback

    def _dumps(obj: Any) -> bytes:
        return json.dumps(
            obj,
            separators=(",", ":"),
            ensure_ascii=False,
            default=_json_default,
        ).encode("utf-8")


def _maybe_envelope(data: Any) -> Any:
    if isinstance(data, Mapping) and ("data" in data or "error" in data):
        return data
    return {"data": data, "ok": True}


ResponseHeaders = Mapping[str, str]


def _with_headers(resp: Response, headers: ResponseHeaders | None) -> Response:
    for key, value in (headers or {}).items():
        resp.headers.append((key.lower(), value))
    return resp


def as_json(
    data: Any,
    *,
    status: int = 200,
    headers: ResponseHeaders | None = None,
    envelope: bool = True,
    dumps=_dumps,
) -> Response:
    payload = _maybe_envelope(data) if envelope else data
    response = Response.from_json(payload, status_code=status)
    response.body = dumps(payload)
    return _with_headers(response, headers)


def as_html(
    html: str, *, status: int = 200, headers: ResponseHeaders | None = None
) -> Response:
    return _with_headers(Response.html(html, status_code=status), headers)


def as_text(
    text: str, *, status: int = 200, headers: ResponseHeaders | None = None
) -> Response:
    return _with_headers(Response.text(text, status_code=status), headers)


def as_redirect(
    url: str, *, status: int = 307, headers: ResponseHeaders | None = None
) -> Response:
    response = Response(
        status_code=status,
        headers=[("location", url)],
        media_type="application/octet-stream",
    )
    return _with_headers(response, headers)


def as_stream(
    chunks: Iterable[bytes] | AsyncIterable[bytes],
    *,
    media_type: str = "application/octet-stream",
    status: int = 200,
    headers: ResponseHeaders | None = None,
) -> Response:
    if hasattr(chunks, "__aiter__"):
        raise TypeError("AsyncIterable streaming is not supported in stdapi shortcuts")
    body_chunks = [bytes(chunk) for chunk in chunks]
    response = Response(
        status_code=status,
        headers=[("content-type", media_type)],
        body=b"".join(body_chunks),
        media_type=media_type,
    )
    return _with_headers(response, headers)


def as_file(
    path: str | Path,
    *,
    filename: str | None = None,
    download: bool = False,
    status: int = 200,
    headers: ResponseHeaders | None = None,
    stat_result: os.stat_result | None = None,
    etag: str | None = None,
    last_modified: datetime | None = None,
) -> Response:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return Response.text("Not Found", status_code=404)

    media_type, _ = mimetypes.guess_type(str(file_path))
    media_type = media_type or "application/octet-stream"
    stat_info = stat_result or os.stat(file_path)
    if etag is None:
        etag = f'W/"{stat_info.st_mtime_ns}-{stat_info.st_size}"'
    modified = last_modified or datetime.fromtimestamp(
        stat_info.st_mtime, tz=timezone.utc
    )

    response = Response(
        status_code=status,
        headers=[("content-type", media_type)],
        body=file_path.read_bytes(),
        media_type=media_type,
    )
    response.headers.append(("etag", etag))
    response.headers.append(
        ("last-modified", modified.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    )
    if download or filename:
        resolved_filename = filename or file_path.name
        response.headers.append(
            ("content-disposition", f'attachment; filename="{resolved_filename}"')
        )
    return _with_headers(response, headers)


__all__ = [
    "Template",
    "Response",
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
]
