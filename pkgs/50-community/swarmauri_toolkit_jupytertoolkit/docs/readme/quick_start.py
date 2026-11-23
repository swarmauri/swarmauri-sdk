from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

toolkit = JupyterToolkit()

# Start a kernel and execute a notebook
start = toolkit.tools["JupyterStartKernelTool"]()
print(start)

run = toolkit.tools["JupyterExecuteNotebookTool"](
    notebook_path="reports/daily.ipynb", timeout=120
)
print(run)

# Export the executed notebook to HTML
export = toolkit.tools["JupyterExportHtmlTool"](
    notebook_path="reports/daily.ipynb", output_path="reports/daily.html"
)
print(export)

# Gracefully shut down the kernel
shutdown = toolkit.tools["JupyterShutdownKernelTool"](
    kernel_id=start["kernel_id"], shutdown_timeout=10
)
print(shutdown)
