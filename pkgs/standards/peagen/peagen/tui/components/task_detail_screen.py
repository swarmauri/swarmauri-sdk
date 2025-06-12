from __future__ import annotations

import json
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class TaskDetailScreen(ModalScreen[None]):
    """Display details of a selected task."""

    def __init__(self, task: dict) -> None:
        super().__init__()
        self.task = task

    def compose(self) -> ComposeResult:  # pragma: no cover - ui code
        yield Center(
            Vertical(
                Static(json.dumps(self.task, indent=2), id="task-json"),
                Button("Close", id="close"),
                id="task-detail-box",
            )
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - ui code
        if event.button.id == "close":
            await self.dismiss()
