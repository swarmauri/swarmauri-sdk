import json  # For pretty printing task details, if needed

from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll  # Assuming these might be used
from textual.reactive import reactive  # Import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static  # Assuming these might be used


class TaskDetailScreen(ModalScreen[None]):
    """A modal screen to display task details."""

    task: reactive[dict | None] = reactive(None)

    def __init__(self, task_data: dict) -> None:
        super().__init__()
        self.task = task_data

    def compose(self) -> ComposeResult:
        task_content = "No task data."
        if self.task is not None:
            try:
                task_content = json.dumps(self.task, indent=2)
            except TypeError:
                task_content = "Error: Task data is not JSON serializable."

        with VerticalScroll(id="task_detail_vertical_scroll"):
            yield Label("Task Details", classes="title")  # Use a class for styling
            yield Static(task_content, id="task_data_display", markup=False)
            yield Center(
                Button("Close", variant="primary", id="close_task_detail_button")
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "close_task_detail_button":
            self.dismiss()
