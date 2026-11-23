from swarmauri_tool_readprocessoutput import ReadProcessOutputTool


# Supply the backend that owns the process session.
def make_tool(backend):
    return ReadProcessOutputTool(backend=backend)
