from swarmauri_tool_containerfeedchars import ContainerFeedCharsTool

tool = ContainerFeedCharsTool(container_name="my-container")
output = tool(command="ls -al")
print(output["stdout"])
