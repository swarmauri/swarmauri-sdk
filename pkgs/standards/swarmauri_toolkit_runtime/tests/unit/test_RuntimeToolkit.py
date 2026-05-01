import pytest

from swarmauri_toolkit_runtime import RuntimeToolkit


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
def test_runtime_add_get_update_remove_runtime_tool():
    toolkit = RuntimeToolkit()

    create_result = toolkit.get_tool_by_name("RegisterRuntimeTool")(
        {
            "type": "AdditionTool",
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
        }
    )
    assert create_result["status"] == "created"

    get_result = toolkit.get_tool_by_name("InspectRuntimeTool")("RuntimeAdditionTool")
    assert get_result["tool"]["name"] == "RuntimeAdditionTool"
    assert get_result["tool_type"] == "AdditionTool"
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
            "type": "AdditionTool",
            "name": "RuntimeAdditionToolV2",
            "description": "Updated runtime addition tool.",
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
        },
    )
    assert update_result["status"] == "updated"
    assert toolkit.get_tool_by_name("RuntimeAdditionToolV2")(4, 7) == {"sum": "11"}

    delete_result = toolkit.get_tool_by_name("UnregisterRuntimeTool")(
        "RuntimeAdditionToolV2"
    )
    assert delete_result["status"] == "deleted"
    with pytest.raises(ValueError, match="not found"):
        toolkit.get_tool_by_name("RuntimeAdditionToolV2")


@pytest.mark.unit
def test_runtime_rejects_reserved_tool_mutation():
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("UnregisterRuntimeTool")("RegisterRuntimeTool")

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(
            {
                "type": "AdditionTool",
                "name": "ListRuntimeTools",
                "parameters": [
                    {
                        "name": "x",
                        "input_type": "integer",
                        "description": "The left operand",
                        "required": True,
                    }
                ],
            }
        )


@pytest.mark.unit
def test_runtime_rejects_registration_without_declared_parameters():
    toolkit = RuntimeToolkit()

    with pytest.raises(ValueError, match="non-empty 'parameters' list"):
        toolkit.get_tool_by_name("RegisterRuntimeTool")(
            {
                "type": "AdditionTool",
                "name": "RuntimeAdditionTool",
                "description": "Adds two integers during the active agent session.",
            }
        )
