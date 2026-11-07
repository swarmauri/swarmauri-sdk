from typing import Dict, Literal

from pydantic import Field

from swarmauri_core.processes import IProcessBackend
from swarmauri_process_docker import DockerProcessBackend
from swarmauri_process_kubernetes import KubernetesProcessBackend
from swarmauri_tool_runcommand import RunCommandTool
from swarmauri_tool_runbashscript import RunBashScriptTool
from swarmauri_tool_readprocessoutput import ReadProcessOutputTool
from swarmauri_tool_writestdin import WriteStdinTool
from swarmauri_tool_cancelprocess import CancelProcessTool
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

from swarmauri_tool_containernewsession import ContainerNewSessionTool
from swarmauri_tool_containerfeedchars import ContainerFeedCharsTool
from swarmauri_tool_containermakepr import ContainerMakePrTool


@ComponentBase.register_type(ToolkitBase, "ContainerToolkit")
class ContainerToolkit(ToolkitBase):
    tools: Dict[str, SubclassUnion[ToolBase]] = Field(
        default_factory=dict, exclude=True
    )
    container_name: str | None = None
    image: str | None = None
    driver: Literal["docker", "kubernetes"] = "docker"

    def __init__(
        self,
        container_name: str | None = None,
        image: str | None = None,
        driver: Literal["docker", "kubernetes"] = "docker",
        backend: IProcessBackend | None = None,
        **kwargs,
    ):
        kwargs.pop("tools", None)
        super().__init__(
            container_name=container_name, image=image, driver=driver, **kwargs
        )
        process_backend = backend
        if process_backend is None:
            process_backend = (
                DockerProcessBackend()
                if driver == "docker"
                else KubernetesProcessBackend()
            )
        self.tools = {
            "ContainerNewSessionTool": ContainerNewSessionTool(
                container_name=container_name,
                image=image,
                driver=driver,
                backend=backend,
            ),
            "ContainerFeedCharsTool": ContainerFeedCharsTool(
                container_name=container_name,
                driver=driver,
                backend=backend,
            ),
            "ContainerMakePrTool": ContainerMakePrTool(
                container_name=container_name,
                driver=driver,
                backend=backend,
            ),
            "RunCommandTool": RunCommandTool(
                backend=process_backend, workspace=container_name
            ),
            "RunBashScriptTool": RunBashScriptTool(
                backend=process_backend, workspace=container_name
            ),
            "ReadProcessOutputTool": ReadProcessOutputTool(
                backend=process_backend
            ),
            "WriteStdinTool": WriteStdinTool(backend=process_backend),
            "CancelProcessTool": CancelProcessTool(backend=process_backend),
        }
