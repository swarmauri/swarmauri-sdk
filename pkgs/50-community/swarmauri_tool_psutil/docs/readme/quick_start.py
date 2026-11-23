from swarmauri_tool_psutil import PsutilTool

tool = PsutilTool()
cpu = tool("cpu")

print(cpu.keys())
