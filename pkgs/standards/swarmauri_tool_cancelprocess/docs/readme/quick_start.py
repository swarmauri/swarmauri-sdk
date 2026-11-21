from swarmauri_tool_cancelprocess import CancelProcessTool


# Supply the backend that owns the process session.
def make_tool(backend):
    return CancelProcessTool(backend=backend)
