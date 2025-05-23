import subprocess
from typing import List, Literal
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

    driver: Literal["docker", "kubernetes"] = "docker"

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="container_name",
                input_type="string",
                description="Target container or pod name",
                required=True,
            ),
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
        ]
    )

    def __call__(self, container_name: str, title: str, body: str) -> dict:
        if self.driver == "docker":
            cmd = [
                "docker",
                "exec",
                container_name,
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
                container_name,
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
