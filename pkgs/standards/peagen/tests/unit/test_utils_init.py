import pytest

from peagen._utils._init import _call_handler, _summary


@pytest.mark.unit
def test_summary_writes_output(capsys, tmp_path):
    _summary(tmp_path, "peagen process")
    out = capsys.readouterr().out
    assert "Scaffold created" in out
    assert str(tmp_path) in out
    assert "peagen process" in out


@pytest.mark.unit
def test_call_handler_invokes_handler(monkeypatch):
    called = {}

    async def fake_handler(task):
        called["payload"] = task.payload
        return {"ok": True}

    monkeypatch.setattr("peagen._utils._init.init_handler", fake_handler)
    monkeypatch.setattr("peagen._utils._init.uuid.uuid4", lambda: "uuid")

    result = _call_handler({"x": 1})
    assert result == {"ok": True}
    assert called["payload"]["args"] == {"x": 1}
