from __future__ import annotations

import base64
import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Union

from .stdapi import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    Response,
)


def _json_default(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, Path):
        return str(value)
    return str(value)


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


JSON = Mapping[str, Any]
Headers = Mapping[str, str]


def _header_pairs(headers: Optional[Headers]) -> list[tuple[str, str]]:
    return [(k.lower(), v) for k, v in (headers or {}).items()]


def as_json(
    data: Any,
    *,
    status: int = 200,
    headers: Optional[Headers] = None,
    envelope: bool = True,
    dumps=_dumps,
) -> Response:
    payload = _maybe_envelope(data) if envelope else data
    body = dumps(payload)
    return Response(
        status_code=status,
        headers=[
            ("content-type", "application/json; charset=utf-8"),
            *_header_pairs(headers),
        ],
        body=body,
    )


def as_html(
    html: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    resp = HTMLResponse(html, status_code=status)
    resp.headers.extend(_header_pairs(headers))
    return resp


def as_text(
    text: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    resp = PlainTextResponse(text, status_code=status)
    resp.headers.extend(_header_pairs(headers))
    return resp


def as_redirect(
    url: str, *, status: int = 307, headers: Optional[Headers] = None
) -> Response:
    hdrs = [("location", url), *_header_pairs(headers)]
    return Response(status_code=status, headers=hdrs, body=b"")


def as_stream(
    chunks: Union[Iterable[bytes], AsyncIterable[bytes]],
    *,
    media_type: str = "application/octet-stream",
    status: int = 200,
    headers: Optional[Headers] = None,
) -> Response:
    if hasattr(chunks, "__aiter__"):
        raise TypeError("Async streams are not supported by stdapi Response")
    body = b"".join(bytes(c) for c in chunks)  # type: ignore[arg-type]
    return Response(
        status_code=status,
        headers=[("content-type", media_type), *_header_pairs(headers)],
        body=body,
    )


def as_file(
    path: Union[str, Path],
    *,
    filename: Optional[str] = None,
    download: bool = False,
    status: int = 200,
    headers: Optional[Headers] = None,
    stat_result: Optional[Any] = None,
    etag: Optional[str] = None,
    last_modified: Optional[datetime] = None,
) -> Response:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return PlainTextResponse("Not Found", status_code=404)
    media_type, _ = mimetypes.guess_type(str(p))
    media_type = media_type or "application/octet-stream"
    hdrs = dict(headers or {})
    st = stat_result or p.stat()
    if etag is None:
        etag = f'W/"{st.st_mtime_ns}-{st.st_size}"'
    lm = last_modified or datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
    hdrs.setdefault("ETag", etag)
    hdrs.setdefault("Last-Modified", lm.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    if download or filename:
        fname = filename or p.name
        hdrs.setdefault("Content-Disposition", f'attachment; filename="{fname}"')
    response = FileResponse(str(p), media_type=media_type)
    response.status_code = status
    response.headers.extend(_header_pairs(hdrs))
    return response


__all__ = [
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
]
