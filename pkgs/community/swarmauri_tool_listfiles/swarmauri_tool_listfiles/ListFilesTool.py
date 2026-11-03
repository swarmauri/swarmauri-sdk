from pathlib import Path
from typing import Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


def _failure(target: Path, message: str) -> Dict[str, object]:
    """The empty result shape carrying an explanatory error."""
    return {
        "path": str(target),
        "count": 0,
        "entries": [],
        "error": message,
    }


@ComponentBase.register_type(ToolBase, "ListFilesTool")
class ListFilesTool(ToolBase):
    """List the files and directories directly inside a folder."""

    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="path",
                input_type="string",
                description=("Directory to list. A leading ~ is expanded."),
                required=True,
            ),
            Parameter(
                name="full_paths",
                input_type="boolean",
                description=(
                    "Include an absolute path for each entry. "
                    "Defaults to false, which returns names only."
                ),
                required=False,
            ),
        ]
    )
    name: str = "ListFilesTool"
    description: str = (
        "Lists the files and directories directly inside a folder, "
        "sorted by name. Does not recurse into subdirectories."
    )
    type: Literal["ListFilesTool"] = "ListFilesTool"

    def __call__(
        self, path: str, full_paths: bool = False
    ) -> Dict[str, object]:
        """
        List the immediate contents of ``path``.

        Parameters:
            path (str): Directory to list. A leading ~ is expanded.
            full_paths (bool): When true each entry also carries an
                absolute "path" key. Defaults to false.

        Returns:
            Dict[str, object]: ``{"path", "count", "entries"}`` on success,
            where each entry is ``{"name", "is_dir"}`` plus ``"path"`` when
            ``full_paths`` is true. On failure the same keys are returned empty
            with an ``"error"`` explaining why.

        Nothing is raised: a missing path, a path that is a file rather than a
        directory, and an unreadable directory are all reported through
        ``error`` so an agent can correct the call.
        """
        target = Path(path).expanduser()

        try:
            if not target.exists():
                return _failure(target, f"{target} does not exist.")
            if not target.is_dir():
                return _failure(
                    target,
                    f"{target} is not a directory. "
                    "This tool lists folders, not files.",
                )
        except OSError as exc:
            # exists() and is_dir() are not total: a path below a directory
            # this process cannot search raises rather than returning False.
            return _failure(target, f"Could not read {target}: {exc}")

        root = target.absolute()
        entries: List[Dict[str, object]] = []

        try:
            for child in target.iterdir():
                entry: Dict[str, object] = {
                    "name": child.name,
                    "is_dir": child.is_dir(),
                }
                if full_paths:
                    # absolute(), not resolve(): the caller asked for the path
                    # of this entry, not of whatever a symlink points at. A
                    # cyclic link also makes resolve() raise RuntimeError,
                    # which no OSError handler would catch.
                    entry["path"] = str(root / child.name)
                entries.append(entry)
        except OSError as exc:
            return _failure(target, f"Could not read {target}: {exc}")

        entries.sort(key=lambda entry: str(entry["name"]).lower())

        return {
            "path": str(target),
            "count": len(entries),
            "entries": entries,
        }
