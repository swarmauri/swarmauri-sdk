import pytest

from peagen.tui.app import QueueDashboardApp


@pytest.mark.unit
def test_pagination_actions(monkeypatch):
    app = QueueDashboardApp()
    monkeypatch.setattr(app, "run_worker", lambda *a, **k: None)
    app.limit = 10
    app.offset = 0
    app.action_next_page()
    assert app.offset == 10
    app.action_prev_page()
    assert app.offset == 0
    app.action_prev_page()
    assert app.offset == 0
    # set limit directly
    app.action_set_limit(20)
    assert app.limit == 20
    # jump to page respecting bounds
    app.queue_len = 30
    app.limit = 10
    app.action_jump_page(3)
    assert app.offset == 20
    app.action_jump_page(99)
    assert app.offset == 20


@pytest.mark.unit
def test_perform_filtering_limit_offset():
    app = QueueDashboardApp()
    tasks = [
        {
            "id": i,
            "pool": "default",
            "status": "running",
            "payload": {"action": "a"},
            "labels": [],
        }
        for i in range(30)
    ]
    result = app._perform_filtering_and_sorting(
        tasks,
        {"collapsed": set()},
        limit=10,
        offset=20,
    )
    ids = [t["id"] for t in result["tasks_to_display"]]
    assert ids == list(range(20, 30))


@pytest.mark.unit
def test_header_page_info():
    app = QueueDashboardApp()

    class DummyFooter:
        def __init__(self) -> None:
            self.page_info = None

        def set_page_info(self, current: int, total: int) -> None:
            self.page_info = (current, total)

    app.footer = DummyFooter()
    data = {
        "tasks_to_display": [],
        "workers_data": [],
        "metrics_data": {
            "queue_len": 50,
            "done_len": 0,
            "fail_len": 0,
            "worker_len": 0,
        },
        "collapsed_state": set(),
    }
    app.limit = 10
    app.offset = 20
    app._update_ui_with_processed_data(data, [])
    assert app.sub_title == "Page 3 of 5"
