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
                description="Initial text content. Defaults to an empty file.",
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

        The call never overwrites: an existing file or directory at the path,
        a missing parent directory, and any OS-level write failure are all
        reported through ``error`` rather than raised, so an agent can read the
        reason and choose another path.
        """
        target = Path(path).expanduser()

        if target.exists():
            return {
                "created": False,
                "path": str(target),
                "error": (
                    f"Something already exists at {target}. "
                    "Nothing was written."
                ),
            }

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
            target.write_text(content, encoding="utf-8")
        except OSError as exc:
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
