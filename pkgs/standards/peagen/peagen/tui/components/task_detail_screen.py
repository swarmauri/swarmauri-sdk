
from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll  # Assuming these might be used
from textual.reactive import reactive  # Import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, DataTable  # Assuming these might be used


class TaskDetailScreen(ModalScreen[None]):
    """A modal screen to display task details."""

    task: reactive[dict | None] = reactive(None)

    def __init__(self, task_data: dict) -> None:
        super().__init__()
        self.task = task_data

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="task_detail_vertical_scroll"):
            yield Label("Task Details", classes="title")  # Use a class for styling

            table = DataTable(id="task_detail_table")
            table.add_columns("Key", "Value")

            if isinstance(self.task, dict):
                for key in sorted(self.task):
                    table.add_row(str(key), str(self.task[key]))

            yield table

            yield Center(
                Button("Close", variant="primary", id="close_task_detail_button")
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "close_task_detail_button":
            self.dismiss()
