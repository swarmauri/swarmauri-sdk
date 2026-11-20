from swarmauri_tool_runbashscript import RunBashScriptTool


# Supply the backend that owns the process session.
def make_tool(backend):
    return RunBashScriptTool(backend=backend)
