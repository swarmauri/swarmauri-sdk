import pytest
from peagen.tui.app import QueueDashboardApp


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ws_event_triggers_refresh(monkeypatch):
    app = QueueDashboardApp()

    called = {}

    def fake_trigger(debounce=True):
        called["count"] = called.get("count", 0) + 1

    monkeypatch.setattr(app, "trigger_data_processing", fake_trigger)

    await app.handle_ws_event({"type": "task.update", "data": {"id": "1"}})

    assert called.get("count") == 1
