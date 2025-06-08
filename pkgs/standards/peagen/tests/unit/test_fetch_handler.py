import pytest
from pathlib import Path

from peagen.handlers import fetch_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_handler_passes_args(monkeypatch):
    captured = {}

    def fake_fetch_many(**kwargs):
        captured.update(kwargs)
        return {"count": len(kwargs.get("manifest_uris", []))}

    monkeypatch.setattr(handler, "fetch_many", fake_fetch_many)

    args = {
        "manifests": ["m1", "m2"],
        "out_dir": "~/out",
        "no_source": True,
        "install_template_sets": False,
    }

    result = await handler.fetch_handler({"payload": {"args": args}})

    assert result == {"count": 2}
    assert captured["manifest_uris"] == ["m1", "m2"]
    assert captured["out_dir"] == Path("~/out").expanduser()
    assert captured["no_source"] is True
    assert captured["install_template_sets_flag"] is False
