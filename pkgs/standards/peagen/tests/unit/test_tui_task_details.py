import pytest
from textual.coordinate import Coordinate
from textual.app import App
from textual.widgets import DataTable
from peagen.tui.components.task_detail_screen import TaskDetailScreen

from peagen.tui.app import QueueDashboardApp


class DummyScreen:
    def __init__(self, task_data=None, task=None):
        self.task = task_data if task_data is not None else task


class DummyTable:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def get_row_at(self, row):  # old API path
        class Row:
            key = self.key
        return Row()

    def get_cell_at(self, row, col):
        return self.value


class DummyEvent:
    def __init__(self, table, value):
        self.data_table = table
        self.value = value
        self.coordinate = Coordinate(0, 0)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_click_task_row_opens_detail(monkeypatch):
    app = QueueDashboardApp()
    app.backend.tasks = [{"id": "42"}]
    app.tasks_table = DummyTable("42", "42")
    app.err_table = DummyTable("x", "x")

    monkeypatch.setattr("peagen.tui.app.TaskDetailScreen", DummyScreen)

    captured = {}

    async def fake_push(screen):
        captured["screen"] = screen

    monkeypatch.setattr(app, "push_screen", fake_push)

    event = DummyEvent(app.tasks_table, "42")

    await app.on_data_table_cell_selected(event)

    assert isinstance(captured.get("screen"), DummyScreen)
    assert captured["screen"].task["id"] == "42"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_click_error_row_opens_detail(monkeypatch):
    app = QueueDashboardApp()
    app.backend.tasks = [{"id": "99"}]
    app.err_table = DummyTable("99", "99")
    app.tasks_table = DummyTable("y", "y")

    monkeypatch.setattr("peagen.tui.app.TaskDetailScreen", DummyScreen)

    captured = {}

    async def fake_push(screen):
        captured["screen"] = screen

    monkeypatch.setattr(app, "push_screen", fake_push)

    event = DummyEvent(app.err_table, "99")

    await app.on_data_table_cell_selected(event)

    assert isinstance(captured.get("screen"), DummyScreen)
    assert captured["screen"].task["id"] == "99"


@pytest.mark.unit
@pytest.mark.asyncio
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
async def test_on_select_changed_updates_filters(select_id, attr, value):
    app = QueueDashboardApp()

    class DummySelect:
        def __init__(self, sid):
            self.id = sid

    class DummyChanged:
        def __init__(self, sid, val):
            self.select = DummySelect(sid)
            self.control = self.select
            self.value = val

        def stop(self):
            pass

    event = DummyChanged(select_id, value)
    await app.on_select_changed(event)
    assert getattr(app, attr) == value

@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_detail_compose_rows():
    task = {"a": 1, "b": 2, "c": 3}

    class TestApp(App):
        def compose(self):
            yield TaskDetailScreen(task_data=task)

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen_stack[-1]
        table = screen.query_one(DataTable)
        assert len(table.rows) == len(task)
