import pytest

from peagen.tui.app import QueueDashboardApp


class DummyTable:
    def __init__(self, key):
        self.key = key
        self.cursor_row = 0

    def get_row_key(self, row):
        return self.key


@pytest.mark.unit
def test_default_collapsed(monkeypatch):
    parent = {"id": "p1", "result": {"children": ["c1"]}}
    child = {"id": "c1"}
    app = QueueDashboardApp()
    app.backend.tasks = [parent, child]
    app.client.tasks = {}
    app.tasks_table = DummyTable("p1")

    import asyncio

    asyncio.run(app.async_process_and_update_data())

    assert "p1" in app.collapsed
