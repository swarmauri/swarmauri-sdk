from __future__ import annotations

from .response_spec import ResponseKind, ResponseSpec, TemplateSpec

# Backward-compatible aliases kept in spec space to avoid core->concrete coupling.
Template = TemplateSpec
Response = ResponseSpec

__all__ = [
    "TemplateSpec",
    "ResponseSpec",
    "ResponseKind",
    "Template",
    "Response",
]
