import pytest
from textual.coordinate import Coordinate
from textual.events import Click
from rich.style import Style

from peagen.tui.app import QueueDashboardApp


class DummyScreen:
    def __init__(self, task_data):
        self.task = task_data


class DummyTable:
    def __init__(self, key):
        self.key = key
        self.cb = None
        self.style = Style(meta={"row": 0, "column": 0})

    async def _on_click(self, event: Click) -> None:
        if event.chain == 2 and self.cb:
            await self.cb(self.key)

    def get_row_at(self, row):
        class Row:
            key = self.key

        return Row()

    def get_cell_at(self, row, col):
        return self.key


class DummyEvent:
    def __init__(self, table):
        self.data_table = table
        self.value = table.key
        self.coordinate = Coordinate(0, 0)
        self.style = Style(meta={"row": 0, "column": 0})
        self.chain = 2

    def stop(self):
        pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_double_click_task_row_opens_detail(monkeypatch):
    app = QueueDashboardApp()
    app.backend.tasks = [{"id": "42"}]
    table = DummyTable("42")
    table.cb = app.open_task_detail
    app.tasks_table = table
    app.err_table = DummyTable("x")

    monkeypatch.setattr("peagen.tui.app.TaskDetailScreen", DummyScreen)

    captured = {}

    async def fake_push(screen):
        captured["screen"] = screen

    monkeypatch.setattr(app, "push_screen", fake_push)

    event = Click(table, 0, 0, 0, 0, 1, False, False, False, style=table.style, chain=2)
    await table._on_click(event)

    assert isinstance(captured.get("screen"), DummyScreen)
    assert captured["screen"].task["id"] == "42"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_double_click_error_row_opens_detail(monkeypatch):
    app = QueueDashboardApp()
    app.backend.tasks = [{"id": "99"}]
    table = DummyTable("99")
    table.cb = app.open_task_detail
    app.err_table = table
    app.tasks_table = DummyTable("y")

    monkeypatch.setattr("peagen.tui.app.TaskDetailScreen", DummyScreen)

    captured = {}

    async def fake_push(screen):
        captured["screen"] = screen

    monkeypatch.setattr(app, "push_screen", fake_push)

    event = Click(table, 0, 0, 0, 0, 1, False, False, False, style=table.style, chain=2)
    await table._on_click(event)

    assert isinstance(captured.get("screen"), DummyScreen)
    assert captured["screen"].task["id"] == "99"


@pytest.mark.unit
@pytest.mark.parametrize(
    "select_id,attr,value",
    [
        ("filter_id", "filter_id", "42"),
        ("filter_pool", "filter_pool", "default"),
        ("filter_status", "filter_status", "done"),
        ("filter_action", "filter_action", "process"),
        ("filter_label", "filter_label", "foo"),
    ],
)
def test_on_select_changed_updates_filters(select_id, attr, value):
    app = QueueDashboardApp()

    class DummySelect:
        def __init__(self, sid):
            self.id = sid

    class DummyInput:
        def __init__(self, sid):
            self.id = sid

    class DummyChanged:
        def __init__(self, control, val):
            self._control = control
            self.value = val

        def stop(self):
            pass

        @property
        def control(self):
            return self._control

        @property
        def input(self):
            return self._control

    control_cls = DummyInput if select_id == "filter_id" else DummySelect
    control = control_cls(select_id)
    event = DummyChanged(control, value)
    import asyncio

    if select_id == "filter_id":
        asyncio.run(app.on_input_changed(event))
    else:
        asyncio.run(app.on_select_changed(event))
    assert getattr(app, attr) == value
