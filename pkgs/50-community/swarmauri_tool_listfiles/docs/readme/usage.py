from pathlib import Path

from swarmauri_tool_listfiles import ListFilesTool

# Use a directory that exists; the tool lists what is there and does not
# create anything.
Path("/tmp/project").mkdir(parents=True, exist_ok=True)
Path("/tmp/project/README.md").write_text("x", encoding="utf-8")
Path("/tmp/project/src").mkdir(exist_ok=True)

tool = ListFilesTool(allowed_roots=["/tmp/project"])

result = tool(path="/tmp/project")
# {
#   "path": "/tmp/project",
#   "count": 2,
#   "entries": [
#     {"name": "README.md", "is_dir": False},
#     {"name": "src", "is_dir": True},
#   ],
# }

result = tool(path="/tmp/project", full_paths=True)
# {"name": "README.md", "is_dir": False, "path": "/tmp/project/README.md"}
