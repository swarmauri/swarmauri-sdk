"""Concrete JSON response primitive."""

from __future__ import annotations

import json as json_module
from typing import Any

from ._response import Response


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


__all__ = ["JSONResponse"]
