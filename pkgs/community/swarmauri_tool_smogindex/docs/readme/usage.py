from swarmauri_tool_smogindex import SMOGIndexTool

tool = SMOGIndexTool()
result = tool(
    "This is a sample text with complex sentences and polysyllabic words."
)

print(result["smog_index"])
