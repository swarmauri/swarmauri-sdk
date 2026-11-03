import fnmatch
import os
from pathlib import Path
from typing import Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "FindFileTool")
class FindFileTool(ToolBase):
    """Find files under a directory by name or wildcard pattern."""

    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="path",
                input_type="string",
                description=("Directory to search. A leading ~ is expanded."),
                required=True,
            ),
            Parameter(
                name="pattern",
                input_type="string",
                description=(
                    "Shell-style wildcard matched case-insensitively "
                    "against each file name, for example *.log or report?.txt."
                ),
                required=True,
            ),
            Parameter(
                name="recursive",
                input_type="boolean",
                description=(
                    "Also search subdirectories. Defaults to false, which "
                    "checks only the top level."
                ),
                required=False,
            ),
        ]
    )
    name: str = "FindFileTool"
    description: str = (
        "Searches a directory for files whose name matches a shell-style "
        "wildcard, case-insensitively, optionally walking subdirectories."
    )
    type: Literal["FindFileTool"] = "FindFileTool"

    def __call__(
        self, path: str, pattern: str, recursive: bool = False
    ) -> Dict[str, object]:
        """
        Find files under ``path`` whose name matches ``pattern``.

        Parameters:
            path (str): Root directory to search. A leading ~ is expanded.
            pattern (str): Shell-style wildcard such as ``*.log`` or
                ``report?.txt``, matched case-insensitively against the file
                name only, not the whole path.
            recursive (bool): Walk subdirectories. Defaults to false.

        Returns:
            Dict[str, object]: ``{"path", "pattern", "count", "matches"}`` on
            success, where ``matches`` holds absolute paths in sorted order.
            The same keys are returned empty with an ``error`` when the
            directory is missing, is not a directory, or cannot be read.

        Symbolic links are listed but never followed, so a link cycle cannot
        make the walk run forever. Directories are not returned; this tool
        answers "which files match", not "what is here".
        """
        target = Path(path).expanduser()

        if not target.exists():
            return self._failure(target, pattern, f"{target} does not exist.")

        if not target.is_dir():
            return self._failure(
                target,
                pattern,
                f"{target} is not a directory. This tool searches folders.",
            )

        lowered = pattern.lower()
        matches: List[str] = []

        try:
            if recursive:
                for root, _dirs, files in os.walk(target, followlinks=False):
                    matches.extend(
                        os.path.join(root, name)
                        for name in files
                        if fnmatch.fnmatch(name.lower(), lowered)
                    )
            else:
                matches.extend(
                    str(child)
                    for child in target.iterdir()
                    if child.is_file()
                    and fnmatch.fnmatch(child.name.lower(), lowered)
                )
        except OSError as exc:
            return self._failure(
                target, pattern, f"Could not read {target}: {exc}"
            )

        matches.sort()

        return {
            "path": str(target),
            "pattern": pattern,
            "count": len(matches),
            "matches": matches,
        }

    def _failure(
        self, target: Path, pattern: str, message: str
    ) -> Dict[str, object]:
        """Return the empty result shape with an explanatory error."""
        return {
            "path": str(target),
            "pattern": pattern,
            "count": 0,
            "matches": [],
            "error": message,
        }
