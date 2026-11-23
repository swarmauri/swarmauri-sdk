from swarmauri_toolkit_runtime import RuntimeToolkit

toolkit = RuntimeToolkit()

toolkit.get_tool_by_name("RegisterRuntimeTool")(
    {
        "type": "RuntimeAdditionTool",
        "name": "RuntimeAdditionTool",
        "description": "Adds two integers during the active agent session.",
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
)

result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2, 3)
print(result)
