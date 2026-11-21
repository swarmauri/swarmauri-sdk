from swarmauri_tool_jupyterexecuteandconvert import (
    JupyterExecuteAndConvertTool,
)

tool = JupyterExecuteAndConvertTool()
result = tool(
    notebook_path="reports/weekly.ipynb",
    output_format="html",
    execution_timeout=300,
)

print(result)
