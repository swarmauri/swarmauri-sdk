from __future__ import annotations

from .._concrete._response import Response as _Response
from .._concrete._response import Template as _Template


class Template(_Template):
    """Public concrete template configuration."""


class Response(_Response):
    """Public concrete response configuration."""


__all__ = ["Template", "Response"]
