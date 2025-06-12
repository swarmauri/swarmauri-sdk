from __future__ import annotations

from datetime import datetime
from typing import Mapping

from textual.widgets import DataTable


class WorkersView(DataTable):
    """Display active pools and workers."""

    def update_workers(self, workers: Mapping[str, datetime]) -> None:
        """Refresh the table contents."""
        if not self.columns:
            self.add_columns("Worker", "Last Seen")
        self.clear()
        for name, ts in workers.items():
            self.add_row(name, ts.isoformat(timespec="seconds"))

