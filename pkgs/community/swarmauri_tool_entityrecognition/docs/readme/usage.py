import json
from swarmauri_tool_entityrecognition import EntityRecognitionTool

tool = EntityRecognitionTool()
result = tool(
    text="Apple Inc. is an American multinational technology company."
)
entities = json.loads(result["entities"])
print(entities)
