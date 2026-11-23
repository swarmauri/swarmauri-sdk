import sys
from swarmauri_tool_subprocess import SubprocessTool

tool = SubprocessTool()
result = tool([sys.executable, "-c", "print('hello')"], timeout=5)
assert result["stdout"].strip() == "hello"
assert result["exit_code"] == 0
