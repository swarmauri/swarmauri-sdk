from swarmauri_tool_jupytergetiopubmessage import JupyterGetIOPubMessageTool

channels_url = "ws://localhost:8888/api/kernels/<kernel-id>/channels"
result = JupyterGetIOPubMessageTool()(channels_url, timeout=3.0)

print("stdout:", result["stdout"])
print("stderr:", result["stderr"])
print("logs:", result["logs"])
print("timeout?", result["timeout_exceeded"])
