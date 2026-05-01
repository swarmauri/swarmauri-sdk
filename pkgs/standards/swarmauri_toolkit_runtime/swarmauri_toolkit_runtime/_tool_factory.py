from importlib import import_module
from typing import Any, Mapping

from swarmauri_base.tools.ToolBase import ToolBase


def build_tool_from_spec(tool_spec: Mapping[str, Any] | ToolBase) -> ToolBase:
    if isinstance(tool_spec, ToolBase):
        return tool_spec
    if not isinstance(tool_spec, Mapping):
        raise TypeError("tool_spec must be a mapping or ToolBase instance")

    tool_data = dict(tool_spec)
    tool_type = tool_data.get("type")
    if not isinstance(tool_type, str) or not tool_type:
        raise ValueError("tool_spec must include a non-empty string 'type' field")

    try:
        module = import_module(f"swarmauri.tools.{tool_type}")
    except ModuleNotFoundError as exc:
        raise ValueError(f"Unable to resolve tool type '{tool_type}'") from exc

    tool_cls = getattr(module, tool_type, None)
    if tool_cls is None:
        raise ValueError(
            f"Module for tool type '{tool_type}' does not expose that class"
        )
    if not issubclass(tool_cls, ToolBase):
        raise TypeError(f"Resolved class '{tool_type}' is not a ToolBase subtype")

    return tool_cls.model_validate(tool_data)
