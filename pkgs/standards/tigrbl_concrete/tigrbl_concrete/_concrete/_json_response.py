"""Concrete JSON response primitive."""

from __future__ import annotations

import json as json_module
import importlib.util as _importlib_util
from typing import Any

from ._response import Response

_HAS_ORJSON = _importlib_util.find_spec("orjson") is not None
if _HAS_ORJSON:
    import orjson as _orjson  # type: ignore[import-not-found]


class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200) -> None:
        if _HAS_ORJSON:
            payload = _orjson.dumps(content, default=str)
        else:
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
