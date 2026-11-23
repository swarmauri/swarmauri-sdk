from swarmauri_tool_jupyterexecutenotebookwithparameters import (
    JupyterExecuteNotebookWithParametersTool,
)

tool = JupyterExecuteNotebookWithParametersTool()
result = tool(
    notebook_path="templates/report.ipynb",
    output_notebook_path="artifacts/report-executed.ipynb",
    params={"region": "us", "day": "2026-05-24"},
)

print(result)
