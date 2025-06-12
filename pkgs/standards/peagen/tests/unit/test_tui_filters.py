import datetime
import pytest

from peagen.tui.app import QueueDashboardApp


class DummyTable:
    def __init__(self):
        self.rows = []
        self.columns = []
        self.cursor_row = None
        self.cursor_column = None

    def add_columns(self, *cols):
        self.columns.extend(cols)

    def clear(self):
        self.rows.clear()

    def add_row(self, *row, **kwargs):
        self.rows.append(row)


class DummyWorkersView(DummyTable):
    def update_workers(self, workers):
        self.clear()
        for wid, info in workers.items():
            ts = info.get("last_seen")
            if isinstance(ts, datetime.datetime):
                ts_str = ts.isoformat(timespec="seconds")
            else:
                ts_str = str(ts) if ts is not None else ""
            self.rows.append(
                (
                    wid,
                    str(info.get("pool", "")),
                    str(info.get("url", "")),
                    ts_str,
                )
            )


@pytest.mark.unit
def test_filter_applies_to_all_tabs(monkeypatch):
    app = QueueDashboardApp()
    app.tasks_table = DummyTable()
    app.err_table = DummyTable()
    app.workers_view = DummyWorkersView()

    class Client:
        def __init__(self):
            self.tasks = {
                "t1": {
                    "id": "t1",
                    "pool": "A",
                    "status": "running",
                    "payload": {"action": "foo"},
                    "labels": ["x"],
                    "time": 0,
                },
                "t2": {
                    "id": "t2",
                    "pool": "B",
                    "status": "failed",
                    "payload": {"action": "foo"},
                    "labels": ["y"],
                    "time": 1,
                    "result": {"error": "bad"},
                    "error_file": "/tmp/e",
                },
            }
            now = datetime.datetime.now(datetime.UTC).timestamp()
            self.workers = {
                "w1": {"id": "w1", "pool": "A", "url": "u", "last_seen": now},
                "w2": {"id": "w2", "pool": "B", "url": "u", "last_seen": now},
            }
            self.queues = {"A": 1, "B": 1}

    class Backend:
        tasks = []
        workers = {}

    app.client = Client()
    app.backend = Backend()

    app.filter_pool = "A"
    app.refresh_data()

    assert len(app.tasks_table.rows) == 1
    assert all(row[1] == "A" for row in app.tasks_table.rows)

    assert not app.err_table.rows

    assert len(app.workers_view.rows) == 1
    assert app.workers_view.rows[0][0] == "w1"

