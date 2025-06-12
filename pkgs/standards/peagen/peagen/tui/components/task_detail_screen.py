"""Modal screen for displaying task details in a tree."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Tree


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
            yield Tree("task", id="task_detail_tree")
            yield Center(
                Button("Close", variant="primary", id="close_task_detail_button"),
            )

    def on_mount(self) -> None:
        """Populate the task table when the screen is shown."""

        tree = self.query_one("#task_detail_tree", Tree)
        tree.root.expand()

        if not self.task:
            tree.root.add_leaf("No task data")
            return

        self._populate_tree(tree.root, self.task)

    def _populate_tree(self, node, data) -> None:
        """Recursively populate the tree with task data."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    child = node.add(str(key), expand=True)
                    self._populate_tree(child, value)
                else:
                    node.add_leaf(f"{key}: {value}")
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    child = node.add(f"[{idx}]", expand=True)
                    self._populate_tree(child, item)
                else:
                    node.add_leaf(f"[{idx}] {item}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "close_task_detail_button":
            self.dismiss()
