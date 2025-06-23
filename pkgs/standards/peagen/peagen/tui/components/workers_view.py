from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from textual.widgets import DataTable


class WorkersView(DataTable):
    """Display active pools and workers."""

    def update_workers(self, workers: Mapping[str, Mapping[str, Any]]) -> None:
        """Refresh the table contents."""

        if not self.columns:
            self.add_columns(
                "Worker",
                "Pool",
                "URL",
                "Last Seen",
                "Advertises",
                "Handlers",
            )

        self.clear()
        for wid, info in workers.items():
            ts = info.get("last_seen")
            if isinstance(ts, datetime):
                ts_str = ts.isoformat(timespec="seconds")
            else:
                ts_str = str(ts) if ts is not None else ""

            self.add_row(
                wid,
                str(info.get("pool", "")),
                str(info.get("url", "")),
                ts_str,
                str(info.get("advertises", "")),
                ",".join(info.get("handlers", []))
                if isinstance(info.get("handlers"), list)
                else str(info.get("handlers", "")),
            )
