import fnmatch
import stat
from contextlib import closing
from pathlib import Path
from typing import Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter

from . import _filesystem


@ComponentBase.register_type(ToolBase, "FindFileTool")
class FindFileTool(ToolBase):
    """Find files under a directory by name or wildcard pattern."""

    version: str = "0.1.dev1"
    allowed_roots: List[str] = Field(
        default_factory=lambda: [str(Path.cwd())],
        description="Trusted absolute directories set by the service owner.",
    )
    max_scanned_entries: int = Field(default=100_000, ge=1)
    max_results: int = Field(default=10_000, ge=1)
    max_return_bytes: int = Field(default=1024 * 1024, ge=1)
    max_elapsed_seconds: float = Field(default=2.0, gt=0, allow_inf_nan=False)
    max_depth: int = Field(default=64, ge=0)
    max_pattern_length: int = Field(default=1024, ge=1)
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
        """Find bounded regular-file matches through trusted directory handles.

        Matching is case-insensitive against basenames. Symlinks and special
        files are excluded in both modes. Failures return no partial matches.
        """
        display = path if isinstance(path, str) else ""
        try:
            if not isinstance(path, str) or not path.strip():
                raise ValueError("path must be a non-empty string")
            if (
                not isinstance(pattern, str)
                or not pattern
                or "\x00" in pattern
            ):
                raise ValueError(
                    "pattern must be a non-empty string without NULs"
                )
            if len(pattern) > self.max_pattern_length:
                raise ValueError("pattern exceeds the configured length limit")
            if not isinstance(recursive, bool):
                raise ValueError("recursive must be a boolean")
            target = Path(path).expanduser().absolute()
            display = str(target)
            budget = _filesystem.Budget(
                self.max_scanned_entries,
                self.max_results,
                self.max_return_bytes,
                self.max_elapsed_seconds,
            )
            lowered = pattern.lower()
            matches = []

            def walk(descriptor, current, relative, depth):
                with closing(
                    _filesystem.directory_entries(descriptor)
                ) as children:
                    for name, mode in children:
                        budget.visit()
                        if mode is None:
                            continue
                        if stat.S_ISREG(mode):
                            if fnmatch.fnmatchcase(name.lower(), lowered):
                                match = str(current / name)
                                budget.retain(match)
                                matches.append(match)
                        elif recursive and stat.S_ISDIR(mode):
                            if depth >= self.max_depth:
                                raise ValueError(
                                    "Scan exceeded the directory-depth limit"
                                )
                            with _filesystem.child_directory(
                                descriptor, name, root_fd, relative / name
                            ) as child:
                                walk(
                                    child,
                                    current / name,
                                    relative / name,
                                    depth + 1,
                                )

            with _filesystem.open_directory(target, self.allowed_roots) as (
                descriptor,
                root_fd,
                relative,
            ):
                walk(descriptor, target, relative, 0)
            matches.sort()
            result = {
                "path": display,
                "pattern": pattern,
                "count": len(matches),
                "matches": matches,
            }
            budget.finish(result)
            return result
        except FileNotFoundError:
            return self._failure(display, pattern, "Directory does not exist.")
        except NotADirectoryError:
            return self._failure(display, pattern, "Path is not a directory.")
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            return self._failure(
                display, pattern, f"Could not read directory: {exc}"
            )

    def _failure(self, target, pattern, message) -> Dict[str, object]:
        return _filesystem.failure_response(
            {
                "path": str(target),
                "pattern": pattern if isinstance(pattern, str) else "",
                "count": 0,
                "matches": [],
                "error": message,
            },
            self.max_return_bytes,
        )
