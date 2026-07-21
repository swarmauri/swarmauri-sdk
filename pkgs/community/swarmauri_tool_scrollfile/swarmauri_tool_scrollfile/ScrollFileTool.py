from collections import deque
from typing import Deque, List, Literal, Optional, TypedDict

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

    lines: List[ScrollLine]
    start_line: int
    end_line: Optional[int]
    page_size: int
    has_previous: bool
    has_next: bool
    previous_start_line: Optional[int]
    next_start_line: Optional[int]


@ComponentBase.register_type(ToolBase, "ScrollFileTool")
class ScrollFileTool(ToolBase):
    """Read a bounded, navigable page from a UTF-8 text file."""

    version: str = "0.1.0"
    name: str = "ScrollFileTool"
    description: str = (
        "Reads a bounded range of numbered lines from a UTF-8 text file and "
        "provides previous and next page positions."
    )
    type: Literal["ScrollFileTool"] = "ScrollFileTool"  # type: ignore[assignment]
    parameters: List[Parameter] = Field(  # type: ignore[assignment]
        default_factory=lambda: [
            Parameter(
                name="file_path",
                input_type="string",
                description="Path to the UTF-8 text file to read.",
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
            file_path=file_path,
            target_start=target_start,
            page_size=read_size,
        )

        if page:
            actual_start = page[0]["line_number"]
            end_line: Optional[int] = page[-1]["line_number"]
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
        if direction not in {"up", "down"}:
            raise ValueError("direction must be either 'up' or 'down'.")

    @staticmethod
    def _read_page(
        file_path: str, target_start: int, page_size: int
    ) -> tuple[List[ScrollLine], bool]:
        preceding: Deque[ScrollLine] = deque(maxlen=page_size)
        window: List[ScrollLine] = []

        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line: ScrollLine = {
                    "line_number": line_number,
                    "content": raw_line.rstrip("\r\n"),
                }
                if line_number < target_start:
                    preceding.append(line)
                    continue

                window.append(line)
                if len(window) > page_size:
                    break

        if not window and preceding:
            return list(preceding), False

        return window[:page_size], len(window) > page_size
