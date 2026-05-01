import pytest

from swarmauri_toolkit_toolcrudtoolkit import ToolCrudToolkit


@pytest.mark.unit
def test_toolcrudtoolkit_resource():
    toolkit = ToolCrudToolkit()
    assert toolkit.resource == "Toolkit"


@pytest.mark.unit
def test_toolcrudtoolkit_type():
    toolkit = ToolCrudToolkit()
    assert toolkit.type == "ToolCrudToolkit"


@pytest.mark.unit
def test_toolcrudtoolkit_bootstraps_management_tools():
    toolkit = ToolCrudToolkit()
    listing = toolkit.get_tool_by_name("ListToolkitToolsTool")()

    assert listing["tool_count"] == 5
    assert "AddToolToToolkitTool" in listing["tool_names"]
    assert "UpdateToolInToolkitTool" in listing["tool_names"]


@pytest.mark.unit
def test_toolcrudtoolkit_add_get_update_remove_runtime_tool():
    toolkit = ToolCrudToolkit()

    create_result = toolkit.get_tool_by_name("AddToolToToolkitTool")(
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

    get_result = toolkit.get_tool_by_name("GetToolFromToolkitTool")(
        "RuntimeAdditionTool"
    )
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

    update_result = toolkit.get_tool_by_name("UpdateToolInToolkitTool")(
        "RuntimeAdditionTool",
        {
            "type": "AdditionTool",
            "name": "RuntimeAdditionToolV2",
            "description": "Updated runtime addition tool.",
        },
    )
    assert update_result["status"] == "updated"
    assert toolkit.get_tool_by_name("RuntimeAdditionToolV2")(4, 7) == {"sum": "11"}

    delete_result = toolkit.get_tool_by_name("RemoveToolFromToolkitTool")(
        "RuntimeAdditionToolV2"
    )
    assert delete_result["status"] == "deleted"
    with pytest.raises(ValueError, match="not found"):
        toolkit.get_tool_by_name("RuntimeAdditionToolV2")


@pytest.mark.unit
def test_toolcrudtoolkit_rejects_reserved_tool_mutation():
    toolkit = ToolCrudToolkit()

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("RemoveToolFromToolkitTool")("AddToolToToolkitTool")

    with pytest.raises(ValueError, match="reserved"):
        toolkit.get_tool_by_name("AddToolToToolkitTool")(
            {
                "type": "AdditionTool",
                "name": "ListToolkitToolsTool",
            }
        )
