from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

tool = JupyterShutdownKernelTool()
result = tool(kernel_id="example-kernel-id", shutdown_timeout=5)

print(result)
