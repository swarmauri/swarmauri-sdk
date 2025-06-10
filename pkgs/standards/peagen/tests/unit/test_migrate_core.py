import pytest
from pathlib import Path

from peagen.core import migrate_core


@pytest.mark.unit
def test_alembic_upgrade_invokes_subprocess(monkeypatch, tmp_path: Path):
    calls = {}

    def fake_run(cmd, check):
        calls["cmd"] = cmd

    monkeypatch.setattr(migrate_core.subprocess, "run", fake_run)

    cfg = tmp_path / "al.ini"
    result = migrate_core.alembic_upgrade(cfg)

    assert result == {"ok": True}
    assert calls["cmd"] == ["alembic", "-c", str(cfg), "upgrade", "head"]


@pytest.mark.unit
def test_alembic_revision_invokes_subprocess(monkeypatch, tmp_path: Path):
    calls = {}

    def fake_run(cmd, check):
        calls["cmd"] = cmd

    monkeypatch.setattr(migrate_core.subprocess, "run", fake_run)

    cfg = tmp_path / "al.ini"
    result = migrate_core.alembic_revision("msg", cfg)

    assert result == {"ok": True}
    assert calls["cmd"] == [
        "alembic",
        "-c",
        str(cfg),
        "revision",
        "--autogenerate",
        "-m",
        "msg",
    ]
