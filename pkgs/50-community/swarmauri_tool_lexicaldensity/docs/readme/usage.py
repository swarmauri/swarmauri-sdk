from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()
result = tool(
    "This report summarizes quarterly revenue growth across segments."
)

print(result["lexical_density"])
