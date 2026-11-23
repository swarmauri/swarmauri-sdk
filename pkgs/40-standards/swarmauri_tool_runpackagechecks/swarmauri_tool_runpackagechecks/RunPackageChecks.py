from collections.abc import Callable
from pathlib import PurePosixPath
from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.processes import (
    IProcessBackend,
    ProcessEvent,
    ProcessRequest,
)


@ComponentBase.register_type(ToolBase, "RunPackageChecks")
class RunPackageChecks(ToolBase):
    """Run the standard member checks and stream output to a host callback."""

    name: str = "RunPackageChecks"
    description: str = "Run Ruff and pytest checks for an allowed SDK member."
    type: Literal["RunPackageChecks"] = "RunPackageChecks"
    backend: IProcessBackend = Field(exclude=True)
    workspace: str | None = None
    cwd: str | None = None
    members: dict[str, str]
    timeout: float = Field(default=300, gt=0)
    on_output: Callable[[ProcessEvent], None] | None = Field(
        default=None, exclude=True
    )
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="package",
                input_type="string",
                description="Allowed package name",
                required=True,
            ),
            ParameterBase(
                name="fix",
                input_type="boolean",
                description="Apply Ruff fixes and formatting",
                required=False,
            ),
        ]
    )

    def __call__(self, package: str, fix: bool = False) -> dict:
        member = PurePosixPath(self.members[package])
        if (
            member.is_absolute()
            or ".." in member.parts
            or member.parts[:1] != ("pkgs",)
        ):
            raise ValueError("Member must be a relative path under pkgs")
        prefix = (
            "uv",
            "run",
            "--directory",
            str(member),
            "--package",
            package,
        )
        checks = [
            (*prefix, "ruff", "format", *(() if fix else ("--check",)), "."),
            (*prefix, "ruff", "check", *(("--fix",) if fix else ()), "."),
            (*prefix, "pytest"),
        ]
        results = []
        for argv in checks:
            result = self._run(argv)
            results.append(result)
            if result["exit_code"] != 0 or result["outcome"] != "exited":
                return {"status": "failed", "checks": results}
        return {"status": "passed", "checks": results}

    def _run(self, argv):
        handle = self.backend.start(
            ProcessRequest(
                argv,
                cwd=self.cwd,
                workspace=self.workspace,
                timeout=self.timeout,
            )
        )
        self.backend.write_stdin(handle, b"", close=True)
        cursor = 0
        output = bytearray()
        truncated = False
        while True:
            page = self.backend.read(handle, after=cursor, wait=1)
            cursor = page.cursor
            truncated |= page.truncated
            for event in page.events:
                if self.on_output is not None:
                    self.on_output(event)
                if event.kind == "exit":
                    self.backend.release(handle)
                    return {
                        "argv": argv,
                        "exit_code": event.exit_code,
                        "outcome": event.outcome,
                        "truncated": truncated,
                        "output": output.decode(errors="replace"),
                    }
                output.extend(event.data)
                if len(output) > 16384:
                    del output[:-16384]
                    truncated = True
