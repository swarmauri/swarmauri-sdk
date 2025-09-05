from __future__ import annotations

from typing import Any, Dict, Iterable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Select

from peagen.orm import Status


class FilterBar(Horizontal):
    """Dropdown filters for the dashboard."""

    def __init__(self) -> None:
        super().__init__()
        self._select_widget_configs: Dict[Select, Dict[str, Any]] = {}

        select_definitions = [
            {
                "name": "pool_select",
                "prompt": "pool",
                "filter_id": "filter_pool",
                "allow_blank": True,
            },
            {
                "name": "status_select",
                "prompt": "status",
                "filter_id": "filter_status",
                "allow_blank": True,
            },
            {
                "name": "action_select",
                "prompt": "action",
                "filter_id": "filter_action",
                "allow_blank": True,
            },
            {
                "name": "label_select",
                "prompt": "label",
                "filter_id": "filter_label",
                "allow_blank": True,
            },
        ]

        for definition in select_definitions:
            select_widget = Select(
                [],
                prompt=definition["prompt"],
                allow_blank=definition["allow_blank"],
                id=definition["filter_id"],
                compact=True,
            )
            select_widget.styles.width = 20
            setattr(self, definition["name"], select_widget)
            self._select_widget_configs[select_widget] = {
                "allow_blank": definition["allow_blank"]
            }

        self.id_input = Input(placeholder="task id", id="filter_id", compact=True)
        self.id_input.styles.width = 40

    def compose(self) -> ComposeResult:
        yield self.id_input
        yield self.pool_select
        yield self.status_select
        yield self.action_select
        yield self.label_select

    def _get_select_allow_blank(self, select: Select) -> bool:
        return self._select_widget_configs.get(select, {}).get("allow_blank", False)

    def _set_options(self, select: Select, values: Iterable[str]) -> None:
        current_value_before_update = select.value

        options_list = [(str(v), str(v)) for v in sorted(set(values)) if v is not None]
        select.set_options(options_list)

        select_allows_blank = self._get_select_allow_blank(select)

        if (
            current_value_before_update is not None
            and current_value_before_update != Select.BLANK
            and any(
                opt_val == current_value_before_update for _, opt_val in options_list
            )
        ):
            select.value = current_value_before_update
        elif not select_allows_blank and options_list:
            if select.value == Select.BLANK or not any(
                opt_val == select.value for _, opt_val in options_list
            ):
                select.value = options_list[0][1]
        elif select_allows_blank:
            if select.value != Select.BLANK and not any(
                opt_val == select.value for _, opt_val in options_list
            ):
                select.value = Select.BLANK
            elif not options_list:
                select.value = Select.BLANK

    def update_options(self, tasks: Iterable[dict]) -> None:
        pools = {str(t.get("pool")) for t in tasks if t.get("pool") is not None}
        statuses = {status.value for status in Status}
        actions = {
            str(t.get("action"))
            for t in tasks
            if t.get("action") is not None
        }
        labels = {
            str(lbl) for t in tasks for lbl in t.get("labels", []) if lbl is not None
        }

        if not self.pool_select.expanded:
            self._set_options(self.pool_select, pools)
        if not self.status_select.expanded:
            self._set_options(self.status_select, statuses)
        if not self.action_select.expanded:
            self._set_options(self.action_select, actions)
        if not self.label_select.expanded:
            self._set_options(self.label_select, labels)

    def clear(self) -> None:
        for select_widget in (
            self.pool_select,
            self.status_select,
            self.action_select,
            self.label_select,
        ):
            if self._get_select_allow_blank(select_widget):
                select_widget.value = Select.BLANK
        self.id_input.value = ""
