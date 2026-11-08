from swarmauri_base.processes import ContainerProcessBackendBase
from swarmauri_process_subprocess import SubprocessBackend


class DockerProcessBackend(ContainerProcessBackendBase):
    """Run and control processes in a docker workspace."""

    def __init__(self, *, transport=None):
        super().__init__(
            transport if transport is not None else SubprocessBackend()
        )

    def _exec(self, workspace, argv, interactive=False):
        flags = ("-i",) if interactive else ()
        return ("docker", "exec", *flags, "--", workspace, *argv)

    def open_workspace(self, name: str, image: str) -> str:
        return self._control(
            (
                "docker",
                "run",
                "-d",
                "--name",
                name,
                "--",
                image,
                "sleep",
                "infinity",
            )
        )

    def close_workspace(self, name: str) -> None:
        self._control(("docker", "rm", "-f", "--", name))
