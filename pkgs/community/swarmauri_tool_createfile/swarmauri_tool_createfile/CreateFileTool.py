from pathlib import Path
from typing import Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "CreateFileTool")
class CreateFileTool(ToolBase):
    """Create a new text file at a path, optionally with initial content."""

    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="path",
                input_type="string",
                description=(
                    "Path of the file to create. A leading ~ is expanded."
                ),
                required=True,
            ),
            Parameter(
                name="content",
                input_type="string",
                description=(
                    "Initial text content. Defaults to an empty file."
                ),
                required=False,
            ),
        ]
    )
    name: str = "CreateFileTool"
    description: str = (
        "Creates a new text file at the given path with optional initial "
        "content. Refuses to overwrite an existing file."
    )
    type: Literal["CreateFileTool"] = "CreateFileTool"

    def __call__(self, path: str, content: str = "") -> Dict[str, object]:
        """
        Create a file at ``path`` holding ``content``.

        Parameters:
            path (str): Destination path. A leading ~ is expanded to the home
                directory.
            content (str): Text written as UTF-8. Defaults to "".

        Returns:
            Dict[str, object]: On success ``{"created": True, "path": ...,
            "bytes_written": ...}``. On a refused write ``{"created": False,
            "path": ..., "error": ...}``.

        The creation is atomic. The destination is opened in exclusive-create
        mode, so an existing file and a dangling symlink both fail here rather
        than being truncated by a later write; checking existence first and
        writing afterwards would leave a window between the two, and a
        dangling symlink reads as free to ``exists()``.

        Nothing is raised: a missing parent directory, an occupied path, and
        an OS-level write failure are all reported through ``error`` so an
        agent can read the reason and choose another path.
        """
        target = Path(path).expanduser()

        if not target.parent.exists():
            return {
                "created": False,
                "path": str(target),
                "error": (
                    f"The directory {target.parent} does not exist. "
                    "Create it first or choose another path."
                ),
            }

        try:
            handle = target.open("x", encoding="utf-8", newline="")
        except FileExistsError:
            return {
                "created": False,
                "path": str(target),
                "error": (
                    f"Something already exists at {target}. "
                    "Nothing was written."
                ),
            }
        except OSError as exc:
            return {
                "created": False,
                "path": str(target),
                "error": f"Could not create {target}: {exc}",
            }

        try:
            with handle:
                handle.write(content)
        except OSError as exc:
            # This call created the file, so removing it cannot destroy data
            # belonging to anyone else. Leaving a partial file behind would
            # also make the caller's retry fail as "already exists".
            try:
                target.unlink()
            except OSError:
                pass
            return {
                "created": False,
                "path": str(target),
                "error": f"Could not write {target}: {exc}",
            }

        return {
            "created": True,
            "path": str(target),
            "bytes_written": target.stat().st_size,
        }
