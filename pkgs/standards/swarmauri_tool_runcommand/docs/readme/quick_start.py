from swarmauri_tool_runcommand import RunCommandTool


# Supply the backend that owns the process session.
def make_tool(backend):
    return RunCommandTool(backend=backend)
