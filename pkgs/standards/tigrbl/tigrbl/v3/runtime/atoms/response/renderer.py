from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Mapping, Optional, Union, cast
import logging

from ....deps.starlette import BackgroundTask, Response

from ....response.shortcuts import (
    as_file,
    as_html,
    as_json,
    as_stream,
    as_text,
)

JSON = Mapping[str, Any]

logger = logging.getLogger("uvicorn")


@dataclass
class ResponseHints:
    media_type: Optional[str] = None
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    filename: Optional[str] = None
    download: bool = False
    etag: Optional[str] = None
    last_modified: Optional[Any] = None
    background: Optional[BackgroundTask] = None


class ResponseKind:
    JSON = "application/json"
    HTML = "text/html"
    TEXT = "text/plain"
    FILE = "application/file"
    STREAM = "application/stream"
    REDIRECT = "application/redirect"


ResponseLike = Union[
    Response,
    bytes,
    bytearray,
    memoryview,
    str,
    Path,
    JSON,
    Iterable[bytes],
    AsyncIterable[bytes],
]


def render(
    request: Any,
    payload: ResponseLike,
    *,
    hints: Optional[ResponseHints] = None,
    default_media: str = "application/json",
    envelope_default: bool = False,
) -> Response:
    logger.debug("Rendering response with payload type %s", type(payload))
    if isinstance(payload, Response):
        return payload

    hints = hints or ResponseHints()
    chosen = hints.media_type or default_media

    if isinstance(payload, Path):
        return as_file(
            payload,
            filename=hints.filename,
            download=hints.download,
            status=hints.status_code,
            headers=hints.headers,
        )

    if isinstance(payload, (bytes, bytearray, memoryview)):
        return as_stream(
            iter((bytes(payload),)),
            media_type="application/octet-stream",
            status=hints.status_code,
            headers=hints.headers,
        )

    if hasattr(payload, "__aiter__") or (
        hasattr(payload, "__iter__") and not isinstance(payload, (str, dict, list))
    ):
        return as_stream(
            cast(Union[Iterable[bytes], AsyncIterable[bytes]], payload),
            media_type="application/octet-stream",
            status=hints.status_code,
            headers=hints.headers,
        )

    if isinstance(payload, str):
        if payload.lstrip().startswith("<") or chosen == "text/html":
            return as_html(payload, status=hints.status_code, headers=hints.headers)
        return as_text(payload, status=hints.status_code, headers=hints.headers)

    return as_json(
        payload,
        status=hints.status_code,
        headers=hints.headers,
        envelope=envelope_default,
    )


__all__ = [
    "ResponseHints",
    "ResponseKind",
    "ResponseLike",
    "render",
]
