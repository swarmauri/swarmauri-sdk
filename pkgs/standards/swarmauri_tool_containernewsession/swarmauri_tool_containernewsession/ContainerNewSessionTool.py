import subprocess
from typing import List, Literal
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "ContainerNewSessionTool")
class ContainerNewSessionTool(ToolBase):
    """Start a new container session."""

    version: str = "1.0.0"
    name: str = "ContainerNewSessionTool"
    description: str = "Start a new Docker or Kubernetes container running a shell."
    type: Literal["ContainerNewSessionTool"] = "ContainerNewSessionTool"

    driver: Literal["docker", "kubernetes"] = "docker"

    container_name: str | None = Field(
        default=None, description="Name for the container or pod"
    )
    image: str | None = Field(default=None, description="Container image to launch")

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="container_name",
                input_type="string",
                description="Name for the container or pod",
                required=False,
            ),
            Parameter(
                name="image",
                input_type="string",
                description="Container image to launch",
                required=False,
            ),
        ]
    )

    def __call__(
        self, container_name: str | None = None, image: str | None = None
    ) -> dict:
        name = container_name or self.container_name
        img = image or self.image
        if name is None or img is None:
            raise ValueError("container_name and image must be provided")
        if self.driver == "docker":
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                name,
                img,
                "sleep",
                "infinity",
            ]
        else:
            cmd = [
                "kubectl",
                "run",
                name,
                "--image",
                img,
                "-i",
                "--restart=Never",
                "--command",
                "--",
                "sleep",
                "infinity",
            ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return {"session_name": name, "stdout": result.stdout.strip()}
