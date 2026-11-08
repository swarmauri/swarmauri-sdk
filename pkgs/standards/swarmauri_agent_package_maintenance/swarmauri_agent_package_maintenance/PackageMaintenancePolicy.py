def package_maintenance_policy(tool, arguments) -> str:
    """Require review before writes or arbitrary commands."""
    if tool.name == "RunPackageChecks":
        return "ask" if arguments.get("fix", False) else "allow"
    if tool.name in {
        "RunCommandTool",
        "RunBashScriptTool",
        "WriteStdinTool",
        "ContainerMakePrTool",
    }:
        return "ask"
    return "allow"
