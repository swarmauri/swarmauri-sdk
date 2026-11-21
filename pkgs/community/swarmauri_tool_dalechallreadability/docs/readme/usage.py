from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

tool = DaleChallReadabilityTool()
result = tool(
    {"input_text": "This is a simple sentence for testing purposes."}
)

print(result["dale_chall_score"])
