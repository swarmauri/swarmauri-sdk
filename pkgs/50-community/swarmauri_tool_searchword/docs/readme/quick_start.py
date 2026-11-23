from swarmauri_tool_searchword import SearchWordTool

tool = SearchWordTool()
result = tool(file_path="docs/README.md", search_word="swarmauri")

print(result["count"])
