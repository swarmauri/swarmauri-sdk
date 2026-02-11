from __future__ import annotations

import base64
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Union

from ..response.stdapi import (
    FileResponse as StdFileResponse,
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
    hdrs = dict(headers or {})
    hdrs.setdefault("content-type", "application/json; charset=utf-8")
    return Response(status_code=status, headers=list(hdrs.items()), body=body)


def as_html(
    html: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    response = HTMLResponse(html, status_code=status)
    if headers:
        response.headers.extend((k.lower(), v) for k, v in headers.items())
    return response


def as_text(
    text: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    response = PlainTextResponse(text, status_code=status)
    if headers:
        response.headers.extend((k.lower(), v) for k, v in headers.items())
    return response


def as_redirect(
    url: str, *, status: int = 307, headers: Optional[Headers] = None
) -> Response:
    hdrs = dict(headers or {})
    hdrs["location"] = url
    return Response(status_code=status, headers=list(hdrs.items()), body=b"")


def as_stream(
    chunks: Union[Iterable[bytes], AsyncIterable[bytes]],
    *,
    media_type: str = "application/octet-stream",
    status: int = 200,
    headers: Optional[Headers] = None,
) -> Response:
    if hasattr(chunks, "__aiter__"):
        raise TypeError("Async stream responses are not supported in stdapi mode.")
    payload = b"".join(chunks)
    hdrs = dict(headers or {})
    hdrs.setdefault("content-type", media_type)
    return Response(status_code=status, headers=list(hdrs.items()), body=payload)


def as_file(
    path: Union[str, Path],
    *,
    filename: Optional[str] = None,
    download: bool = False,
    status: int = 200,
    headers: Optional[Headers] = None,
    stat_result: Optional[os.stat_result] = None,
    etag: Optional[str] = None,
    last_modified: Optional[datetime] = None,
) -> Response:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return PlainTextResponse("Not Found", status_code=404)
    media_type, _ = mimetypes.guess_type(str(p))
    media_type = media_type or "application/octet-stream"
    hdrs = dict(headers or {})
    st = stat_result or os.stat(p)
    if etag is None:
        etag = f'W/"{st.st_mtime_ns}-{st.st_size}"'
    lm = last_modified or datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
    hdrs.setdefault("etag", etag)
    hdrs.setdefault("last-modified", lm.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    if download or filename:
        fname = filename or p.name
        hdrs.setdefault("content-disposition", f'attachment; filename="{fname}"')
    response = StdFileResponse(str(p), media_type=media_type)
    response.status_code = status
    response.headers.extend((k.lower(), v) for k, v in hdrs.items())
    return response


__all__ = [
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
]
