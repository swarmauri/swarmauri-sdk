from __future__ import annotations

from ..specs.response_spec import ResponseSpec, TemplateSpec


class Template(TemplateSpec):
    """Concrete template configuration used at runtime."""


class Response(ResponseSpec):
    """Concrete response configuration used at runtime."""


__all__ = ["Template", "Response"]
