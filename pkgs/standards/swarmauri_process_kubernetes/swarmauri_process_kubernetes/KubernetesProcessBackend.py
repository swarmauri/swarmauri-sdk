from swarmauri_base.processes import ContainerProcessBackendBase
from swarmauri_process_subprocess import SubprocessBackend


class KubernetesProcessBackend(ContainerProcessBackendBase):
    """Run and control processes in a kubernetes workspace."""

    def __init__(self, *, namespace: str | None = None, transport=None):
        super().__init__(
            transport if transport is not None else SubprocessBackend()
        )
        self._command = (
            ("kubectl", "-n", namespace) if namespace else ("kubectl",)
        )

    def _exec(self, workspace, argv, interactive=False):
        flags = ("-i",) if interactive else ()
        return (*self._command, "exec", *flags, workspace, "--", *argv)

    def open_workspace(self, name: str, image: str) -> str:
        output = self._control(
            (
                *self._command,
                "run",
                name,
                "--image",
                image,
                "--restart=Never",
                "--command",
                "--",
                "sleep",
                "infinity",
            )
        )
        self._control(
            (
                *self._command,
                "wait",
                "--for=condition=Ready",
                f"pod/{name}",
                "--timeout=25s",
            )
        )
        return output

    def close_workspace(self, name: str) -> None:
        self._control(
            (
                *self._command,
                "delete",
                "pod",
                "--ignore-not-found=true",
                "--grace-period=2",
                "--timeout=25s",
                "--",
                name,
            )
        )
