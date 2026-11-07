from contextlib import closing
import stat
from pathlib import Path
from typing import Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter

from . import _filesystem


def _failure(target: Path, message: str, limit: int) -> Dict[str, object]:
    """The empty result shape carrying an explanatory error."""
    return _filesystem.failure_response(
        {
            "path": str(target),
            "count": 0,
            "entries": [],
            "error": message,
        },
        limit,
    )


@ComponentBase.register_type(ToolBase, "ListFilesTool")
class ListFilesTool(ToolBase):
    """List the files and directories directly inside a folder."""

    version: str = "0.1.dev1"
    allowed_roots: List[str] = Field(
        default_factory=lambda: [str(Path.cwd())],
        description="Trusted absolute directories set by the service owner.",
    )
    max_scanned_entries: int = Field(default=100_000, ge=1)
    max_results: int = Field(default=10_000, ge=1)
    max_return_bytes: int = Field(default=1024 * 1024, ge=1)
    max_elapsed_seconds: float = Field(default=2.0, gt=0, allow_inf_nan=False)
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
        """List bounded entries under trusted roots without following links.

        Symlinks have is_dir=False. Returned paths identify the
        entries themselves. Exceeding a limit returns an error.
        """
        display = path if isinstance(path, str) else ""
        try:
            if not isinstance(path, str) or not path.strip():
                raise ValueError("path must be a non-empty string")
            if not isinstance(full_paths, bool):
                raise ValueError("full_paths must be a boolean")
            target = Path(path).expanduser().absolute()
            display = str(target)
            budget = _filesystem.Budget(
                self.max_scanned_entries,
                self.max_results,
                self.max_return_bytes,
                self.max_elapsed_seconds,
            )
            entries = []
            with _filesystem.open_directory(
                target, self.allowed_roots
            ) as descriptor:
                with closing(
                    _filesystem.directory_entries(descriptor)
                ) as children:
                    for name, mode in children:
                        budget.visit()
                        if mode is None:
                            continue
                        entry = {"name": name, "is_dir": stat.S_ISDIR(mode)}
                        if full_paths:
                            entry["path"] = str(target / name)
                        budget.retain(entry)
                        entries.append(entry)
            entries.sort(
                key=lambda entry: (entry["name"].lower(), entry["name"])
            )
            result = {
                "path": display,
                "count": len(entries),
                "entries": entries,
            }
            budget.finish(result)
            return result
        except FileNotFoundError:
            return _failure(
                display, "Directory does not exist.", self.max_return_bytes
            )
        except NotADirectoryError:
            return _failure(
                display,
                "Path is not a directory.",
                self.max_return_bytes,
            )
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            return _failure(
                display,
                f"Could not read directory: {exc}",
                self.max_return_bytes,
            )
