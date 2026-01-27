from __future__ import annotations
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Union
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import mimetypes
import base64

from ..deps.starlette import (
    JSONResponse,
    HTMLResponse,
    PlainTextResponse,
    StreamingResponse,
    FileResponse as StarletteFileResponse,
    RedirectResponse,
    Response,
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
            # Fallback for older orjson builds missing optional flags
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


def as_json(
    data: Any,
    *,
    status: int = 200,
    headers: Optional[Headers] = None,
    envelope: bool = True,
    dumps=_dumps,
) -> Response:
    payload = _maybe_envelope(data) if envelope else data
    try:
        return JSONResponse(
            payload,
            status_code=status,
            headers=dict(headers or {}),
            dumps=lambda o: dumps(o).decode(),
        )
    except TypeError:  # pragma: no cover - starlette >= 0.44
        return Response(
            dumps(payload),
            status_code=status,
            headers=dict(headers or {}),
            media_type="application/json",
        )


def as_html(
    html: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    return HTMLResponse(html, status_code=status, headers=dict(headers or {}))


def as_text(
    text: str, *, status: int = 200, headers: Optional[Headers] = None
) -> Response:
    return PlainTextResponse(text, status_code=status, headers=dict(headers or {}))


def as_redirect(
    url: str, *, status: int = 307, headers: Optional[Headers] = None
) -> Response:
    return RedirectResponse(url, status_code=status, headers=dict(headers or {}))


def as_stream(
    chunks: Union[Iterable[bytes], AsyncIterable[bytes]],
    *,
    media_type: str = "application/octet-stream",
    status: int = 200,
    headers: Optional[Headers] = None,
) -> Response:
    return StreamingResponse(
        chunks, media_type=media_type, status_code=status, headers=dict(headers or {})
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
    hdrs = dict(headers or {})
    st = stat_result or os.stat(p)
    if etag is None:
        etag = f'W/"{st.st_mtime_ns}-{st.st_size}"'
    lm = last_modified or datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
    hdrs.setdefault("ETag", etag)
    hdrs.setdefault("Last-Modified", lm.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    if download or filename:
        fname = filename or p.name
        hdrs.setdefault("Content-Disposition", f'attachment; filename="{fname}"')
    return StarletteFileResponse(
        str(p),
        status_code=status,
        media_type=media_type,
        filename=filename,
        headers=hdrs,
    )


__all__ = [
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
]
