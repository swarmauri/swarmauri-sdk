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
