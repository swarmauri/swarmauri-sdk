# ruff: noqa: N999

import os
import stat
import time
from collections import deque
from pathlib import Path
from typing import ClassVar, Literal, TypedDict

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class ScrollLine(TypedDict):
    """One line returned by :class:`ScrollFileTool`."""

    line_number: int
    content: str


class ScrollResult(TypedDict):
    """A bounded page of file content and its navigation metadata."""

    lines: list[ScrollLine]
    start_line: int
    end_line: int | None
    page_size: int
    has_previous: bool
    has_next: bool
    previous_start_line: int | None
    next_start_line: int | None


@ComponentBase.register_type(ToolBase, "ScrollFileTool")
class ScrollFileTool(ToolBase):
    """Read a bounded, navigable page from a UTF-8 text file."""

    MAX_PAGE_SIZE: ClassVar[int] = 100
    MAX_SCANNED_LINES: ClassVar[int] = 100_000
    MAX_SCANNED_BYTES: ClassVar[int] = 8 * 1024 * 1024
    MAX_LINE_BYTES: ClassVar[int] = 64 * 1024
    MAX_RETURN_BYTES: ClassVar[int] = 256 * 1024
    MAX_ELAPSED_SECONDS: ClassVar[float] = 2.0

    version: str = "0.1.0"
    name: str = "ScrollFileTool"
    description: str = (
        "Reads a bounded range of numbered lines from a UTF-8 text file and "
        "provides previous and next page positions."
    )
    type: Literal["ScrollFileTool"] = "ScrollFileTool"  # type: ignore[assignment]
    allowed_roots: list[str] = Field(
        default_factory=lambda: [str(Path.cwd())],
        description=(
            "Trusted filesystem roots configured by the service owner. "
            "Agent-provided paths must resolve within one of these roots."
        ),
    )
    allow_symlinks: bool = Field(
        default=False,
        description="Privileged opt-in allowing symlinks in requested paths.",
    )
    allow_unrestricted_paths: bool = Field(
        default=False,
        description=(
            "Privileged opt-in allowing paths outside allowed_roots. "
            "Use only inside a least-privilege filesystem sandbox."
        ),
    )
    parameters: list[Parameter] = Field(  # type: ignore[assignment]
        default_factory=lambda: [
            Parameter(
                name="file_path",
                input_type="string",
                description=(
                    "Path to a UTF-8 text file within a service-configured "
                    "allowed root."
                ),
                required=True,
            ),
            Parameter(
                name="start_line",
                input_type="number",
                description=(
                    "One-based page anchor. Down reads from this line; up "
                    "reads the preceding page. Defaults to 1."
                ),
                required=False,
            ),
            Parameter(
                name="page_size",
                input_type="number",
                description="Maximum lines to return. Defaults to 10.",
                required=False,
            ),
            Parameter(
                name="direction",
                input_type="string",
                description="Navigation direction: 'up' or 'down'.",
                required=False,
                enum=["up", "down"],
            ),
        ]
    )

    def __call__(  # type: ignore[override]
        self,
        file_path: str,
        start_line: int = 1,
        page_size: int = 10,
        direction: Literal["up", "down"] = "down",
    ) -> ScrollResult:
        """Return one page of numbered lines and navigation positions.

        ``start_line`` is a one-based page anchor. A downward request starts
        at that line. An upward request returns the page immediately before
        that anchor. Requests beyond the end of a non-empty file clamp to its
        final page so callers can recover without knowing the total line count.
        """
        self._validate_inputs(file_path, start_line, page_size, direction)
        resolved_path = self._resolve_file_path(file_path)

        target_start = (
            start_line
            if direction == "down"
            else max(1, start_line - page_size)
        )
        read_size = (
            min(page_size, start_line - 1)
            if direction == "up" and start_line > 1
            else page_size
        )
        page, has_next = self._read_page(
            file_path=resolved_path,
            target_start=target_start,
            page_size=read_size,
        )

        if page:
            actual_start = page[0]["line_number"]
            end_line: int | None = page[-1]["line_number"]
        else:
            actual_start = 1
            end_line = None

        has_previous = actual_start > 1
        return {
            "lines": page,
            "start_line": actual_start,
            "end_line": end_line,
            "page_size": page_size,
            "has_previous": has_previous,
            "has_next": has_next,
            "previous_start_line": (
                max(1, actual_start - page_size) if has_previous else None
            ),
            "next_start_line": end_line + 1 if has_next and end_line else None,
        }

    @staticmethod
    def _validate_inputs(
        file_path: str,
        start_line: int,
        page_size: int,
        direction: str,
    ) -> None:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string.")
        if (
            not isinstance(start_line, int)
            or isinstance(start_line, bool)
            or start_line < 1
        ):
            raise ValueError("start_line must be a positive integer.")
        if (
            not isinstance(page_size, int)
            or isinstance(page_size, bool)
            or page_size < 1
        ):
            raise ValueError("page_size must be a positive integer.")
        if page_size > ScrollFileTool.MAX_PAGE_SIZE:
            raise ValueError(
                f"page_size cannot exceed {ScrollFileTool.MAX_PAGE_SIZE}."
            )
        if start_line > ScrollFileTool.MAX_SCANNED_LINES:
            raise ValueError(
                "start_line cannot exceed the configured scanned-line limit "
                f"of {ScrollFileTool.MAX_SCANNED_LINES}."
            )
        if direction not in {"up", "down"}:
            raise ValueError("direction must be either 'up' or 'down'.")

    def _resolve_file_path(self, file_path: str) -> Path:
        requested = Path(file_path).expanduser()
        lexical_path = (
            requested if requested.is_absolute() else Path.cwd() / requested
        )

        if not self.allow_symlinks and self._contains_symlink(lexical_path):
            raise PermissionError(
                "file_path must not contain symlinks unless allow_symlinks "
                "is explicitly enabled."
            )

        resolved_path = lexical_path.resolve(strict=True)
        if not self.allow_unrestricted_paths:
            if not self.allowed_roots:
                raise ValueError(
                    "allowed_roots must contain at least one trusted path."
                )
            resolved_roots = [
                Path(root).expanduser().resolve(strict=True)
                for root in self.allowed_roots
            ]
            if not any(
                resolved_path == root or resolved_path.is_relative_to(root)
                for root in resolved_roots
            ):
                raise PermissionError(
                    "file_path resolves outside the configured allowed_roots."
                )

        if not resolved_path.is_file():
            raise ValueError("file_path must resolve to a regular file.")
        return resolved_path

    @staticmethod
    def _contains_symlink(path: Path) -> bool:
        absolute_path = path.absolute()
        return any(
            component.is_symlink()
            for component in reversed((absolute_path, *absolute_path.parents))
        )

    def _read_page(
        self, file_path: Path, target_start: int, page_size: int
    ) -> tuple[list[ScrollLine], bool]:
        preceding: deque[ScrollLine] = deque(maxlen=page_size)
        window: list[ScrollLine] = []
        has_next = False
        scanned_bytes = 0
        returned_bytes = 0
        started_at = time.monotonic()

        flags = os.O_RDONLY
        if not self.allow_symlinks:
            flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(file_path, flags)
        try:
            file_stat = os.fstat(descriptor)
            if not stat.S_ISREG(file_stat.st_mode):
                raise ValueError("file_path must resolve to a regular file.")

            with os.fdopen(descriptor, "rb") as file:
                descriptor = -1
                line_number = 0
                while True:
                    if (
                        time.monotonic() - started_at
                        > self.MAX_ELAPSED_SECONDS
                    ):
                        raise ValueError(
                            "File read exceeded the configured elapsed-time "
                            "limit."
                        )
                    raw_line = file.readline(self.MAX_LINE_BYTES + 1)
                    if not raw_line:
                        break
                    if line_number >= self.MAX_SCANNED_LINES:
                        raise ValueError(
                            "File read exceeded the configured scanned-line "
                            "limit."
                        )
                    line_number += 1
                    if len(raw_line) > self.MAX_LINE_BYTES:
                        raise ValueError(
                            f"Line {line_number} exceeds the configured "
                            "individual-line byte limit."
                        )

                    scanned_bytes += len(raw_line)
                    if scanned_bytes > self.MAX_SCANNED_BYTES:
                        raise ValueError(
                            "File read exceeded the configured scanned-byte "
                            "limit."
                        )

                    content = raw_line.decode("utf-8").rstrip("\r\n")
                    line: ScrollLine = {
                        "line_number": line_number,
                        "content": content,
                    }
                    if line_number < target_start:
                        preceding.append(line)
                        continue

                    if len(window) == page_size:
                        has_next = True
                        break
                    returned_bytes += len(content.encode("utf-8"))
                    if returned_bytes > self.MAX_RETURN_BYTES:
                        raise ValueError(
                            "File page exceeded the configured returned-byte "
                            "limit."
                        )
                    window.append(line)
        finally:
            if descriptor >= 0:
                os.close(descriptor)

        if not window and preceding:
            return list(preceding), False

        return window, has_next
