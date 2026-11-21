from pathlib import Path

from swarmauri_tool_scrollfile import ScrollFileTool

tool = ScrollFileTool(allowed_roots=[str(Path("logs").resolve())])
first_page = tool("logs/application.log")

if first_page["has_next"]:
    second_page = tool(
        "logs/application.log",
        start_line=first_page["next_start_line"],
        page_size=first_page["page_size"],
        direction="down",
    )
