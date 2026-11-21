from pathlib import Path

from swarmauri_tool_findfile import FindFileTool

# Build a small tree so the example is reproducible.
Path("/tmp/logs/archive").mkdir(parents=True, exist_ok=True)
Path("/tmp/logs/app.log").write_text("x", encoding="utf-8")
Path("/tmp/logs/archive/old.log").write_text("x", encoding="utf-8")

tool = FindFileTool(allowed_roots=["/tmp/logs"])

tool(path="/tmp/logs", pattern="*.log")
# {"path": "/tmp/logs", "pattern": "*.log", "count": 1,
#  "matches": ["/tmp/logs/app.log"]}

tool(path="/tmp/logs", pattern="*.log", recursive=True)
# {"count": 2, "matches": ["/tmp/logs/app.log", "/tmp/logs/archive/old.log"]}
