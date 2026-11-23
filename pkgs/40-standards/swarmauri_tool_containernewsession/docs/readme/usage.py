from swarmauri_tool_containernewsession import ContainerNewSessionTool

tool = ContainerNewSessionTool(
    container_name="my-container", image="ubuntu:latest"
)
result = tool()
print(result["stdout"])
