from swarmauri_tool_jupyterruncell import JupyterRunCellTool

tool = JupyterRunCellTool()
result = tool(code="print('hello')", timeout=5)

print(result)
