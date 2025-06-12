from __future__ import annotations

from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Select


class FilterBar(Horizontal):
    """Dropdown filters for the dashboard."""

    def __init__(self) -> None:
        super().__init__()
        self.id_select = Select(prompt="id", allow_blank=True, id="filter_id", compact=True)
        self.pool_select = Select(prompt="pool", allow_blank=True, id="filter_pool", compact=True)
        self.status_select = Select(prompt="status", allow_blank=True, id="filter_status", compact=True)
        self.action_select = Select(prompt="action", allow_blank=True, id="filter_action", compact=True)
        self.label_select = Select(prompt="label", allow_blank=True, id="filter_label", compact=True)

    def compose(self) -> ComposeResult:  # pragma: no cover - UI layout
        yield self.id_select
        yield self.pool_select
        yield self.status_select
        yield self.action_select
        yield self.label_select

    def _set_options(self, select: Select, values: Iterable[str]) -> None:
        current = select.value
        select.set_options([(v, v) for v in sorted(values)])
        if current in {v for _, v in select._options}:  # type: ignore[attr-defined]
            select.value = current

    def update_options(self, tasks: Iterable[dict]) -> None:
        """Rebuild dropdown options from ``tasks``."""
        ids = {str(t.get("id")) for t in tasks if t.get("id") is not None}
        pools = {t.get("pool") for t in tasks if t.get("pool")}
        statuses = {t.get("status") for t in tasks if t.get("status")}
        actions = {t.get("payload", {}).get("action") for t in tasks if t.get("payload", {}).get("action")}
        labels = {lbl for t in tasks for lbl in t.get("labels", [])}
        self._set_options(self.id_select, ids)
        self._set_options(self.pool_select, pools)
        self._set_options(self.status_select, statuses)
        self._set_options(self.action_select, actions)
        self._set_options(self.label_select, labels)

    def clear(self) -> None:
        """Clear all dropdown selections."""
        for select in (
            self.id_select,
            self.pool_select,
            self.status_select,
            self.action_select,
            self.label_select,
        ):
            select.clear()
