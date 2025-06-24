import pytest

from peagen.tui.app import QueueDashboardApp
from peagen.tui.components import DashboardFooter


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


@pytest.mark.unit
def test_set_page_and_limit_updates_offset(monkeypatch):
    app = QueueDashboardApp(limit=10)
    monkeypatch.setattr(app, "run_worker", lambda *a, **k: None)
    app.set_page(3)
    assert app.offset == 20
    app.set_limit(5)
    assert app.limit == 5
    assert app.offset == 0


@pytest.mark.unit
def test_update_page_info(monkeypatch):
    app = QueueDashboardApp(limit=10)
    monkeypatch.setattr(app, "run_worker", lambda *a, **k: None)
    app.footer = DashboardFooter()
    app.backend.total_tasks = 95
    app.offset = 20
    app.update_page_info()
    assert app.footer.page_info == "Page 3/10"
