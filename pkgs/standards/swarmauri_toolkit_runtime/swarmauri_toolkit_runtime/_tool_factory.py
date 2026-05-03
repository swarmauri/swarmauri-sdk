from typing import Any, Mapping

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter

from .DynamicRuntimeTool import DynamicRuntimeTool


def build_tool_from_spec(tool_spec: Mapping[str, Any] | ToolBase) -> ToolBase:
    if isinstance(tool_spec, ToolBase):
        if not tool_spec.parameters:
            raise ValueError("Runtime tool registration requires declared parameters")
        if not callable(getattr(tool_spec, "__call__", None)):
            raise ValueError("Runtime tool registration requires a callable '__call__'")
        return tool_spec
    if not isinstance(tool_spec, Mapping):
        raise TypeError("tool_spec must be a mapping or ToolBase instance")

    tool_data = dict(tool_spec)
    tool_type = tool_data.get("type")
    if not isinstance(tool_type, str) or not tool_type:
        raise ValueError("tool_spec must include a non-empty string 'type' field")
    declared_parameters = tool_data.get("parameters")
    if not isinstance(declared_parameters, list) or not declared_parameters:
        raise ValueError(
            "Runtime tool registration requires a non-empty 'parameters' list"
        )
    call_source = tool_data.get("__call__")
    if not isinstance(call_source, str) or not call_source.strip():
        raise ValueError(
            "Runtime tool registration requires a non-empty '__call__' string"
        )

    tool_data["parameters"] = [
        parameter
        if isinstance(parameter, Parameter)
        else Parameter.model_validate(parameter)
        for parameter in declared_parameters
    ]
    return DynamicRuntimeTool.model_validate(tool_data).validate_call_source()
