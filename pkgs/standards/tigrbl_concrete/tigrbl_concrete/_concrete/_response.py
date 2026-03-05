from __future__ import annotations

from typing import Any, Mapping

from tigrbl_base._base._response_base import ResponseBase, TemplateBase


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


class Template(TemplateBase):
    """Concrete template configuration used at runtime."""


class Response(ResponseBase):
    """Concrete response configuration used at runtime."""


__all__ = ["Template", "Response"]
