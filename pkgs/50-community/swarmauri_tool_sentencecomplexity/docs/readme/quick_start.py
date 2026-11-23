from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

tool = SentenceComplexityTool()
metrics = tool(
    "This is a simple sentence. This is another sentence, with a clause."
)

print(metrics)
