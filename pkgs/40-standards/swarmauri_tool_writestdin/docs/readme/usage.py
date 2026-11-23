from swarmauri_tool_writestdin import WriteStdinTool


# Supply the backend that owns the process session.
def make_tool(backend):
    return WriteStdinTool(backend=backend)
