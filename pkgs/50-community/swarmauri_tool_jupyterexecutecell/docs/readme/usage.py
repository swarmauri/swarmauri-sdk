from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

tool = JupyterExecuteCellTool()
result = tool("print('Hello from Swarmauri')", timeout=30)

print(result)
