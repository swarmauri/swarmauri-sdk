from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

tool = JupyterReadNotebookTool()
result = tool(
    notebook_file_path="notebooks/example.ipynb",
    as_version=4,
)

if "notebook_node" in result:
    notebook = result["notebook_node"]
    print(len(notebook.cells))
else:
    print(result["error"])
