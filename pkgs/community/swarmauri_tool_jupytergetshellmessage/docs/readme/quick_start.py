from swarmauri_tool_jupytergetshellmessage import JupyterGetShellMessageTool

channels_url = "ws://localhost:8888/api/kernels/<kernel-id>/channels"
result = JupyterGetShellMessageTool()(channels_url, timeout=5.0)

if "messages" in result:
    for msg in result["messages"]:
        print(msg)
else:
    print("Error:", result.get("error"))
