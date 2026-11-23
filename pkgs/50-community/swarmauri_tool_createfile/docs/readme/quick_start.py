from pathlib import Path

from swarmauri_tool_createfile import CreateFileTool

# The tool does not create parent directories, so make the parent first.
reports = Path.cwd() / "reports"
reports.mkdir(parents=True, exist_ok=True)

tool = CreateFileTool(allowed_roots=[str(reports)])

result = tool(
    path=str(reports / "summary.txt"),
    content="Quarterly summary\n",
)
# {"created": True, "path": ".../reports/summary.txt", "bytes_written": 18}

# Nothing is written when the path is already taken.
result = tool(path=str(reports / "summary.txt"), content="overwrite attempt")
assert result["created"] is False
