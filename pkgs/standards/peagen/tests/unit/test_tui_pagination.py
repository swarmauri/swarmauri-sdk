import pytest

from peagen.tui.app import QueueDashboardApp


@pytest.mark.unit
def test_pagination_actions():
    app = QueueDashboardApp()
    app.limit = 10
    app.offset = 0
    app.action_next_page()
    assert app.offset == 10
    app.action_prev_page()
    assert app.offset == 0
    app.action_prev_page()
    assert app.offset == 0
