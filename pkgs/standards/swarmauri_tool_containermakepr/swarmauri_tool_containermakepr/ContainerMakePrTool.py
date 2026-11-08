import subprocess
from typing import List, Literal
from swarmauri_base.processes.collect_process import collect_process
from swarmauri_core.processes import IProcessBackend, ProcessRequest

from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "ContainerMakePrTool")
class ContainerMakePrTool(ToolBase):
    """Create a pull request using the gh CLI inside a container."""

    version: str = "1.0.0"
    name: str = "ContainerMakePrTool"
    description: str = "Create a GitHub pull request from a container."
    type: Literal["ContainerMakePrTool"] = "ContainerMakePrTool"

    backend: IProcessBackend | None = Field(default=None, exclude=True)

    driver: Literal["docker", "kubernetes"] = "docker"

    container_name: str | None = Field(
        default=None, description="Target container or pod name"
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="title",
                input_type="string",
                description="Pull request title",
                required=True,
            ),
            Parameter(
                name="body",
                input_type="string",
                description="Pull request body",
                required=True,
            ),
            Parameter(
                name="container_name",
                input_type="string",
                description="Target container or pod name",
                required=False,
            ),
        ]
    )

    def __call__(
        self, title: str, body: str, container_name: str | None = None
    ) -> dict:
        name = container_name or self.container_name
        if name is None:
            raise ValueError("container_name must be provided")
        if self.backend is not None:
            stdout, stderr, event = collect_process(
                self.backend,
                ProcessRequest(
                    ("gh", "pr", "create", "--title", title, "--body", body),
                    workspace=name,
                ),
            )
            if event.exit_code != 0:
                raise RuntimeError(stderr.decode(errors="replace").strip())
            return {"stdout": stdout.decode(errors="replace").strip()}
        if self.driver == "docker":
            cmd = [
                "docker",
                "exec",
                name,
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                body,
            ]
        else:
            cmd = [
                "kubectl",
                "exec",
                name,
                "--",
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                body,
            ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return {"stdout": result.stdout.strip()}
