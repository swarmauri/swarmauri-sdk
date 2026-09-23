import warnings


def __getattr__(name):
    if name == "SubprocessTool":
        warnings.warn(
            "`swarmauri_standard.tools.subprocessTool` is deprecated. "
            "Use `swarmauri_tool_subprocess` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from swarmauri_tool_subprocess import SubprocessTool
        return SubprocessTool
    raise AttributeError(f"module {__name__} has no attribute {name}")