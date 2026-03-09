from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Union,
    cast,
)
import logging

from ...types import ResponseLike

JSON = Mapping[str, Any]

logger = logging.getLogger("uvicorn")


@dataclass
class _RenderedResponse:
    status_code: int = 200
    body: bytes | None = None
    _headers: dict[str, str] = field(default_factory=dict)

    @property
    def raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [
            (str(k).encode("latin-1"), str(v).encode("latin-1"))
            for k, v in self._headers.items()
        ]


@dataclass
class ResponseHints:
    media_type: Optional[str] = None
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    filename: Optional[str] = None
    download: bool = False
    etag: Optional[str] = None
    last_modified: Optional[Any] = None
    background: Optional[Callable[..., Any]] = None


class ResponseKind:
    JSON = "application/json"
    HTML = "text/html"
    TEXT = "text/plain"
    FILE = "application/file"
    STREAM = "application/stream"
    REDIRECT = "application/redirect"


RenderPayloadLike = Union[
    ResponseLike,
    bytes,
    bytearray,
    memoryview,
    str,
    Path,
    JSON,
    Iterable[bytes],
    AsyncIterable[bytes],
]


def _merge_headers(
    base: Mapping[str, str],
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    out = {str(k).lower(): str(v) for k, v in base.items()}
    if extra:
        out.update({str(k).lower(): str(v) for k, v in extra.items()})
    return out


def _as_json(
    data: Any, *, status: int, headers: Mapping[str, str]
) -> _RenderedResponse:
    body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    hdrs = _merge_headers({"content-type": "application/json; charset=utf-8"}, headers)
    return _RenderedResponse(status_code=status, body=body, _headers=hdrs)


def _as_text(
    data: str, *, status: int, headers: Mapping[str, str]
) -> _RenderedResponse:
    hdrs = _merge_headers({"content-type": "text/plain; charset=utf-8"}, headers)
    return _RenderedResponse(
        status_code=status, body=data.encode("utf-8"), _headers=hdrs
    )


def _as_html(
    data: str, *, status: int, headers: Mapping[str, str]
) -> _RenderedResponse:
    hdrs = _merge_headers({"content-type": "text/html; charset=utf-8"}, headers)
    return _RenderedResponse(
        status_code=status, body=data.encode("utf-8"), _headers=hdrs
    )


def _as_stream(
    data: Iterable[bytes] | AsyncIterable[bytes],
    *,
    media_type: str,
    status: int,
    headers: Mapping[str, str],
) -> _RenderedResponse:
    del data
    hdrs = _merge_headers({"content-type": media_type}, headers)
    return _RenderedResponse(status_code=status, body=b"", _headers=hdrs)


def _as_file(
    path: Path,
    *,
    filename: str | None,
    download: bool,
    status: int,
    headers: Mapping[str, str],
) -> _RenderedResponse:
    body = path.read_bytes()
    hdrs = _merge_headers({"content-type": "application/octet-stream"}, headers)
    name = filename or path.name
    if download:
        hdrs["content-disposition"] = f'attachment; filename="{name}"'
    return _RenderedResponse(status_code=status, body=body, _headers=hdrs)


def render(
    request: Any,
    payload: RenderPayloadLike,
    *,
    hints: Optional[ResponseHints] = None,
    default_media: str = "application/json",
    envelope_default: bool = False,
) -> ResponseLike:
    del request, envelope_default
    logger.debug("Rendering response with payload type %s", type(payload))
    if isinstance(payload, ResponseLike):
        return payload

    hints = hints or ResponseHints()
    chosen = hints.media_type or default_media

    if isinstance(payload, Path):
        return _as_file(
            payload,
            filename=hints.filename,
            download=hints.download,
            status=hints.status_code,
            headers=hints.headers,
        )

    if isinstance(payload, (bytes, bytearray, memoryview)):
        return _as_stream(
            iter((bytes(payload),)),
            media_type="application/octet-stream",
            status=hints.status_code,
            headers=hints.headers,
        )

    if hasattr(payload, "__aiter__") or (
        hasattr(payload, "__iter__") and not isinstance(payload, (str, dict, list))
    ):
        return _as_stream(
            cast(Union[Iterable[bytes], AsyncIterable[bytes]], payload),
            media_type="application/octet-stream",
            status=hints.status_code,
            headers=hints.headers,
        )

    if isinstance(payload, str):
        if payload.lstrip().startswith("<") or chosen == "text/html":
            return _as_html(payload, status=hints.status_code, headers=hints.headers)
        return _as_text(payload, status=hints.status_code, headers=hints.headers)

    return _as_json(
        payload,
        status=hints.status_code,
        headers=hints.headers,
    )


__all__ = [
    "ResponseHints",
    "ResponseKind",
    "RenderPayloadLike",
    "render",
]
