import errno
import os
from pathlib import Path
from typing import Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter

from ._paths import open_destination


@ComponentBase.register_type(ToolBase, "CreateFileTool")
class CreateFileTool(ToolBase):
    """Create a UTF-8 file beneath a service-configured trusted root."""

    version: str = "0.1.dev1"
    allowed_roots: List[str] = Field(
        default_factory=lambda: [str(Path.cwd())],
        description="Trusted absolute roots set by the service owner.",
    )
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="path",
                input_type="string",
                description=(
                    "Destination within a root. On POSIX the parent must "
                    "be a configured root. Expands ~."
                ),
                required=True,
            ),
            Parameter(
                name="content",
                input_type="string",
                description="Initial UTF-8 text. Defaults to an empty file.",
                required=False,
            ),
        ]
    )
    name: str = "CreateFileTool"
    description: str = (
        "Creates a new UTF-8 file within configured allowed roots. "
        "Refuses existing destinations, parent traversal, and symlinks."
    )
    type: Literal["CreateFileTool"] = "CreateFileTool"

    def __call__(self, path: str, content: str = "") -> Dict[str, object]:
        """Create without overwriting and report failures as structured values.

        Relative paths are based on the current working directory. The service
        configures allowed_roots; it is not an agent-call parameter. Parent
        directories must already exist. On POSIX the parent must be a
        configured root. UTF-8 is validated before creation.

        Exclusive creation is atomic, but publishing complete content is not.
        On an OS write failure, a partial file may remain. Never unlink the
        final pathname: another process may have replaced that directory entry.
        """
        display_path = path if isinstance(path, str) else ""
        created = False
        try:
            if not isinstance(path, str) or not path.strip():
                raise ValueError("path must be a non-empty string")
            if not isinstance(content, str):
                raise ValueError("content must be a string")
            payload = content.encode("utf-8")
            target = Path(path).expanduser().absolute()
            display_path = str(target)
            descriptor = open_destination(target, self.allowed_roots)
            created = True
            try:
                remaining = memoryview(payload)
                while remaining:
                    count = os.write(descriptor, remaining)
                    if count <= 0:
                        raise OSError(errno.EIO, "Write made no progress")
                    remaining = remaining[count:]
                size = os.fstat(descriptor).st_size
            finally:
                os.close(descriptor)
        except (OSError, ValueError, RuntimeError, TypeError) as exc:
            if isinstance(exc, FileExistsError):
                message = f"Destination already exists: {display_path}"
            elif isinstance(exc, FileNotFoundError):
                message = (
                    "The parent directory does not exist. "
                    "Create it first or choose another path."
                )
            else:
                message = f"Could not create {display_path}: {exc}"
            if created:
                message += (
                    " Partial output may remain. No pathname cleanup occurred "
                    "because the directory entry may have changed."
                )
            return {"created": False, "path": display_path, "error": message}

        return {"created": True, "path": display_path, "bytes_written": size}
