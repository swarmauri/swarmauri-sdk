from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

tool = JupyterExecuteNotebookTool()
executed = tool("notebooks/report.ipynb", timeout=60)

for cell in executed.cells:
    if cell.get("outputs"):
        print(cell["outputs"])
