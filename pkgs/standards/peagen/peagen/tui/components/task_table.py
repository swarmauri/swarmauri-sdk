"""Task table widget with double-click support."""

from __future__ import annotations

from typing import Callable, Awaitable

from textual import events
from textual.widgets import DataTable
from textual.coordinate import Coordinate


class TaskTable(DataTable):
    """Data table that opens task details on double-click."""

    def __init__(self, open_cb: Callable[[str], Awaitable[None]], **kwargs) -> None:
        """Initialize the table.

        Args:
            open_cb: Coroutine called with the task ID when a row is double-clicked.
            **kwargs: Forwarded to ``DataTable``.
        """
        super().__init__(**kwargs)
        self._open_cb = open_cb

    async def _on_click(self, event: events.Click) -> None:  # noqa: D401
        await super()._on_click(event)
        if event.chain != 2:
            return
        meta = event.style.meta
        if "row" not in meta:
            return
        row_index = meta["row"]
        row_key = None
        if hasattr(self, "get_row_key"):
            row_key = self.get_row_key(row_index)
        if row_key is None and hasattr(self, "get_row_at"):
            row_obj = self.get_row_at(row_index)
            row_key = getattr(row_obj, "key", None)
        if row_key is None:
            try:
                cell_value = self.get_cell_at(Coordinate(row_index, 0))
                row_key = str(cell_value).strip()
                if row_key.startswith(("- ", "+ ")):
                    row_key = row_key[2:]
                row_key = row_key.strip()
            except Exception:
                return
        if row_key is not None:
            await self._open_cb(str(row_key))

