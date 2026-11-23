from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = "def add(a: int, b: int = 0) -> int:\n    return a + b\n"
result = tool(source=source, method_name="add")

print(result["signature"])
# def add(a: int, b: int = 0) -> int
