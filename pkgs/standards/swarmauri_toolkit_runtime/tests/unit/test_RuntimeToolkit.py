import pytest

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_toolkit_runtime import RuntimeToolkit
from swarmauri_toolkit_runtime import DynamicRuntimeTool
from swarmauri_toolkit_runtime.InspectRuntimeTool import InspectRuntimeTool
from swarmauri_toolkit_runtime.ListRuntimeTools import ListRuntimeTools
from swarmauri_toolkit_runtime.RegisterRuntimeTool import RegisterRuntimeTool
from swarmauri_toolkit_runtime.ReplaceRuntimeTool import ReplaceRuntimeTool
from swarmauri_toolkit_runtime.UnregisterRuntimeTool import UnregisterRuntimeTool
from swarmauri_toolkit_runtime._tool_factory import build_tool_from_spec


@pytest.fixture
def addition_tool_spec():
    return {
        "type": "RuntimeAdditionTool",
        "name": "RuntimeAdditionTool",
        "description": "Adds two integers during the current session.",
        "parameters": [
            {
                "name": "x",
                "input_type": "integer",
                "description": "The left operand",
                "required": True,
            },
            {
                "name": "y",
                "input_type": "integer",
                "description": "The right operand",
                "required": True,
            },
        ],
        "__call__": '{"sum": str(x + y)}',
    }


def register_addition_tool(toolkit: RuntimeToolkit, tool_spec: dict) -> dict:
    return toolkit.get_tool_by_name("RegisterRuntimeTool")(tool_spec)


@pytest.mark.unit
def test_runtime_resource():
    toolkit = RuntimeToolkit()
    assert toolkit.resource == "Toolkit"


@pytest.mark.unit
def test_runtime_type():
    toolkit = RuntimeToolkit()
    assert toolkit.type == "RuntimeToolkit"


@pytest.mark.unit
def test_runtime_bootstraps_management_tools():
    toolkit = RuntimeToolkit()
    listing = toolkit.get_tool_by_name("ListRuntimeTools")()

    assert listing["tool_count"] == 5
    assert "RegisterRuntimeTool" in listing["tool_names"]
    assert "ReplaceRuntimeTool" in listing["tool_names"]


@pytest.mark.unit
def test_runtime_add_get_update_remove_runtime_tool(addition_tool_spec):
    toolkit = RuntimeToolkit()

    create_result = register_addition_tool(toolkit, addition_tool_spec)
    assert create_result["status"] == "created"
    assert create_result["tool"]["__call__"] == '{"sum": str(x + y)}'

    get_result = toolkit.get_tool_by_name("InspectRuntimeTool")("RuntimeAdditionTool")
    assert get_result["tool"]["name"] == "RuntimeAdditionTool"
    assert get_result["tool_type"] == "RuntimeAdditionTool"
    assert get_result["tool"]["__call__"] == '{"sum": str(x + y)}'
    assert [
        {
            "name": parameter["name"],
            "input_type": parameter["input_type"],
            "description": parameter["description"],
            "required": parameter["required"],
        }
        for parameter in get_result["tool"]["parameters"]
    ] == [
        {
            "name": "x",
            "input_type": "integer",
            "description": "The left operand",
            "required": True,
        },
        {
            "name": "y",
            "input_type": "integer",
            "description": "The right operand",
            "required": True,
        },
    ]

    execution_result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2, 3)
    assert execution_result == {"sum": "5"}

    update_result = toolkit.get_tool_by_name("ReplaceRuntimeTool")(
        "RuntimeAdditionTool",
        {
            "type": "RuntimeAdditionToolV2",
            "name": "RuntimeAdditionToolV2",
            "description": "Updated runtime addition tool.",
            "parameters": addition_tool_spec["parameters"],
            "__call__": '{"sum": str(x + y + 1)}',
        },
    )
    assert update_result["status"] == "updated"
    assert toolkit.get_tool_by_name("RuntimeAdditionToolV2")(4, 7) == {"sum": "12"}

    delete_result = toolkit.get_tool_by_name("UnregisterRuntimeTool")(
        "RuntimeAdditionToolV2"
    )
    assert delete_result["status"] == "deleted"
    with pytest.raises(ValueError, match="not found"):
        toolkit.get_tool_by_name("RuntimeAdditionToolV2")


@pytest.mark.unit
def test_runtime_rejects_reserved_tool_mutation(addition_tool_spec):
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("UnregisterRuntimeTool")("RegisterRuntimeTool")

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(
            {
                **addition_tool_spec,
                "name": "ListRuntimeTools",
                "type": "ListRuntimeTools",
            }
        )


@pytest.mark.unit
def test_runtime_rejects_registration_without_declared_parameters():
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="non-empty 'parameters' list"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(
            {
                "type": "RuntimeAdditionTool",
                "name": "RuntimeAdditionTool",
                "description": "Adds two integers during the active agent session.",
                "__call__": '{"sum": str(x + y)}',
            }
        )


@pytest.mark.unit
def test_runtime_rejects_registration_without_call_source(addition_tool_spec):
    toolkit = RuntimeToolkit()
    invalid_spec = dict(addition_tool_spec)
    invalid_spec.pop("__call__")

    with pytest.raises(ValueError, match="non-empty '__call__' string"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(invalid_spec)


@pytest.mark.unit
def test_runtime_rejects_unsafe_call_source(addition_tool_spec):
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="unsafe syntax|approved builtins|disallowed"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(
            {
                **addition_tool_spec,
                "__call__": '__import__("os").system("whoami")',
            }
        )


@pytest.mark.unit
def test_runtime_rejects_unknown_call_name(addition_tool_spec):
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="disallowed name 'missing_value'"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(
            {
                **addition_tool_spec,
                "__call__": '{"sum": str(missing_value)}',
            }
        )


@pytest.mark.unit
def test_runtime_rejects_missing_required_arguments(addition_tool_spec):
    toolkit = RuntimeToolkit()
    register_addition_tool(toolkit, addition_tool_spec)

    result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2)

    assert result["status"] == "error"
    assert result["error_type"] == "ValueError"
    assert "missing required argument 'y'" in result["error"]


@pytest.mark.unit
def test_runtime_returns_safe_error_for_runtime_failure(addition_tool_spec):
    toolkit = RuntimeToolkit()
    toolkit.get_tool_by_name("RegisterRuntimeTool")(
        {
            **addition_tool_spec,
            "type": "RuntimeDivisionTool",
            "name": "RuntimeDivisionTool",
            "__call__": '{"quotient": x / y}',
        }
    )

    result = toolkit.get_tool_by_name("RuntimeDivisionTool")(3, 0)

    assert result["status"] == "error"
    assert result["tool_name"] == "RuntimeDivisionTool"
    assert result["error_type"] == "ZeroDivisionError"


@pytest.mark.unit
def test_runtime_returns_safe_error_for_base_exception(monkeypatch, addition_tool_spec):
    def crash():
        raise SystemExit("blocked exit")

    monkeypatch.setitem(
        DynamicRuntimeTool.__call__.__globals__["SAFE_BUILTINS"], "crash", crash
    )

    toolkit = RuntimeToolkit()
    toolkit.get_tool_by_name("RegisterRuntimeTool")(
        {
            **addition_tool_spec,
            "type": "RuntimeCrashTool",
            "name": "RuntimeCrashTool",
            "__call__": "crash()",
        }
    )

    result = toolkit.get_tool_by_name("RuntimeCrashTool")(2, 3)

    assert result["status"] == "error"
    assert result["tool_name"] == "RuntimeCrashTool"
    assert result["error_type"] == "SystemExit"
    assert result["error"] == "blocked exit"


@pytest.mark.unit
def test_build_tool_from_spec_rejects_non_mapping():
    with pytest.raises(TypeError, match="mapping or ToolBase"):
        build_tool_from_spec("AdditionTool")


@pytest.mark.unit
def test_build_tool_from_spec_rejects_missing_type(addition_tool_spec):
    invalid_spec = dict(addition_tool_spec)
    invalid_spec.pop("type")

    with pytest.raises(ValueError, match="include a non-empty string 'type'"):
        build_tool_from_spec(invalid_spec)


@pytest.mark.unit
def test_build_tool_from_spec_rejects_empty_call_source(addition_tool_spec):
    invalid_spec = dict(addition_tool_spec)
    invalid_spec["__call__"] = "   "

    with pytest.raises(ValueError, match="non-empty '__call__' string"):
        build_tool_from_spec(invalid_spec)


@pytest.mark.unit
def test_build_tool_from_spec_accepts_tool_instance():
    class InlineTool(ToolBase):
        name: str = "InlineTool"
        description: str = "Inline test tool."
        parameters: list = []
        type: str = "InlineTool"

        def __call__(self):
            return {"ok": True}

    with pytest.raises(ValueError, match="requires declared parameters"):
        build_tool_from_spec(InlineTool())


@pytest.mark.unit
def test_register_runtime_tool_requires_toolkit(addition_tool_spec):
    with pytest.raises(ValueError, match="toolkit is not configured"):
        RegisterRuntimeTool()(addition_tool_spec)


@pytest.mark.unit
def test_register_runtime_tool_rejects_duplicate_name(addition_tool_spec):
    toolkit = RuntimeToolkit()
    register_addition_tool(toolkit, addition_tool_spec)

    with pytest.raises(ValueError, match="already exists"):
        register_addition_tool(toolkit, addition_tool_spec)


@pytest.mark.unit
def test_inspect_runtime_tool_requires_toolkit():
    with pytest.raises(ValueError, match="toolkit is not configured"):
        InspectRuntimeTool()("RuntimeAdditionTool")


@pytest.mark.unit
def test_inspect_runtime_tool_rejects_missing_tool():
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="not found"):
        toolkit.get_tool_by_name("InspectRuntimeTool")("MissingRuntimeTool")


@pytest.mark.unit
def test_list_runtime_tools_requires_toolkit():
    with pytest.raises(ValueError, match="toolkit is not configured"):
        ListRuntimeTools()()


@pytest.mark.unit
def test_list_runtime_tools_serializes_registered_tool(addition_tool_spec):
    toolkit = RuntimeToolkit()
    register_addition_tool(toolkit, addition_tool_spec)

    result = toolkit.get_tool_by_name("ListRuntimeTools")()

    assert "RuntimeAdditionTool" in result["tool_names"]
    assert result["tools"]["RuntimeAdditionTool"]["type"] == "RuntimeAdditionTool"
    assert result["tools"]["RuntimeAdditionTool"]["__call__"] == '{"sum": str(x + y)}'


@pytest.mark.unit
def test_replace_runtime_tool_requires_toolkit(addition_tool_spec):
    with pytest.raises(ValueError, match="toolkit is not configured"):
        ReplaceRuntimeTool()("RuntimeAdditionTool", addition_tool_spec)


@pytest.mark.unit
def test_replace_runtime_tool_rejects_missing_tool(addition_tool_spec):
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="not found"):
        toolkit.get_tool_by_name("ReplaceRuntimeTool")(
            "MissingRuntimeTool", addition_tool_spec
        )


@pytest.mark.unit
def test_replace_runtime_tool_rejects_reserved_replacement_name(addition_tool_spec):
    toolkit = RuntimeToolkit()
    register_addition_tool(toolkit, addition_tool_spec)

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("ReplaceRuntimeTool")(
            "RuntimeAdditionTool",
            {
                **addition_tool_spec,
                "type": "RegisterRuntimeTool",
                "name": "RegisterRuntimeTool",
            },
        )


@pytest.mark.unit
def test_replace_runtime_tool_rejects_name_collision(addition_tool_spec):
    toolkit = RuntimeToolkit()
    register_addition_tool(toolkit, addition_tool_spec)
    register_addition_tool(
        toolkit,
        {
            **addition_tool_spec,
            "type": "RuntimeAdditionToolV2",
            "name": "RuntimeAdditionToolV2",
        },
    )

    with pytest.raises(ValueError, match="already exists"):
        toolkit.get_tool_by_name("ReplaceRuntimeTool")(
            "RuntimeAdditionTool",
            {
                **addition_tool_spec,
                "type": "RuntimeAdditionToolV2",
                "name": "RuntimeAdditionToolV2",
            },
        )


@pytest.mark.unit
def test_unregister_runtime_tool_requires_toolkit():
    with pytest.raises(ValueError, match="toolkit is not configured"):
        UnregisterRuntimeTool()("RuntimeAdditionTool")


@pytest.mark.unit
def test_unregister_runtime_tool_rejects_missing_tool():
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="not found"):
        toolkit.get_tool_by_name("UnregisterRuntimeTool")("MissingRuntimeTool")
