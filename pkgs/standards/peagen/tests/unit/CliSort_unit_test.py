import pytest

from peagen.cli.commands import sort as sort_cmd


@pytest.mark.unit
def test_run_sort_prints(monkeypatch, capsys):
    async def fake_handler(task):
        return {"sorted": ["0) a"]}

    monkeypatch.setattr(sort_cmd, "sort_handler", fake_handler)
    sort_cmd.run_sort("payload.yaml")
    captured = capsys.readouterr()
    assert "0) a" in captured.out
