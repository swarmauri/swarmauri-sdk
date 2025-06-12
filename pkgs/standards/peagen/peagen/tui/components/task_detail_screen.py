"""Modal screen for displaying task details in a table."""

from __future__ import annotations

import json

from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label


class TaskDetailScreen(ModalScreen[None]):
    """A modal screen to display task details."""

    task: reactive[dict | None] = reactive(None)

    def __init__(self, task_data: dict) -> None:
        super().__init__()
        self.task = task_data

    def compose(self) -> ComposeResult:
        """Construct widgets for the detail view."""

        with VerticalScroll(id="task_detail_vertical_scroll"):
            yield Label("Task Details", classes="title")
            yield DataTable(id="task_detail_table")
            yield Center(
                Button("Close", variant="primary", id="close_task_detail_button"),
            )

    def on_mount(self) -> None:
        """Populate the task table when the screen is shown."""

        table = self.query_one("#task_detail_table", DataTable)
        table.add_columns("Key", "Value")

        if not self.task:
            table.add_row("-", "No task data")
            return

        for key, value in self.task.items():
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)
            table.add_row(str(key), value_str)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "close_task_detail_button":
            self.dismiss()
