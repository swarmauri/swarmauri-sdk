from swarmauri_tool_runpackagechecks import RunPackageChecks


def checks_tool(backend):
    return RunPackageChecks(
        backend=backend, members={"swarmauri_core": "pkgs/core"}
    )
