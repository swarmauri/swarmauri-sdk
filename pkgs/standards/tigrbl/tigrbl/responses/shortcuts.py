from __future__ import annotations

import base64
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Union

from ._response import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
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


JSON = Mapping[str, Any]
Headers = Mapping[str, str]


def _with_headers(resp: Response, headers: Optional[Headers]) -> Response:
    for k, v in (headers or {}).items():
        resp.headers.append((k.lower(), v))
    return resp


def as_json(
    data: Any,
    *,
    status: int = 200,
    headers: Optional[Headers] = None,
    envelope: bool = True,
    dumps=_dumps,
) -> Response:
    payload = _maybe_envelope(data) if envelope else data
    resp = JSONResponse(payload, status_code=status)
    resp.body = dumps(payload)
    return _with_headers(resp, headers)


def as_html(
    html: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    return _with_headers(HTMLResponse(html, status_code=status), headers)


def as_text(
    text: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    return _with_headers(PlainTextResponse(text, status_code=status), headers)


def as_redirect(
    url: str, *, status: int = 307, headers: Optional[Headers] = None
) -> Response:
    return _with_headers(RedirectResponse(url, status_code=status), headers)


def as_stream(
    chunks: Union[Iterable[bytes], AsyncIterable[bytes]],
    *,
    media_type: str = "application/octet-stream",
    status: int = 200,
    headers: Optional[Headers] = None,
) -> Response:
    if hasattr(chunks, "__aiter__"):
        raise TypeError("AsyncIterable streaming is not supported in stdapi shortcuts")
    return _with_headers(
        StreamingResponse(chunks, status_code=status, media_type=media_type),
        headers,
    )


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
    st = stat_result or os.stat(p)
    if etag is None:
        etag = f'W/"{st.st_mtime_ns}-{st.st_size}"'
    lm = last_modified or datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)

    resp = FileResponse(str(p), media_type=media_type)
    resp.status_code = status
    resp.headers.append(("etag", etag))
    resp.headers.append(("last-modified", lm.strftime("%a, %d %b %Y %H:%M:%S GMT")))
    if download or filename:
        fname = filename or p.name
        resp.headers.append(("content-disposition", f'attachment; filename="{fname}"'))
    return _with_headers(resp, headers)


__all__ = [
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
]
