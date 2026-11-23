from swarmauri_tool_githubloader import GithubLoadedTool

# Load a tool from GitHub
tool = GithubLoadedTool(
    owner="myorg",
    repo="myrepo",
    path="tools/addition.yaml",
)

# Use like any other tool
result = tool(x=1, y=2)
