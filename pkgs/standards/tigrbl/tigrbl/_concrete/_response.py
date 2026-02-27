from __future__ import annotations

import json as json_module
from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any, Mapping

from ._headers import HeaderCookies, Headers
from .._base.response_base import ResponseBase, TemplateBase


class _JSONDualMethod:
    def __get__(self, obj: "Response" | None, owner: type["Response"]):
        if obj is None:

            def _factory(
                data: Any,
                status_code: int = 200,
                headers: Mapping[str, str] | None = None,
            ) -> "Response":
                return owner.from_json(data, status_code=status_code, headers=headers)

            return _factory

        def _instance_json() -> Any:
            return obj.json_body()

        return _instance_json


@dataclass
class Template(TemplateBase):
    """Concrete template configuration used at runtime."""


@dataclass
class Response(ResponseBase):
    """Concrete response configuration used at runtime."""

__all__ = ["Template", "Response"]
