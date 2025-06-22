import pytest
from pathlib import Path

from peagen.core import migrate_core


@pytest.mark.unit
def test_alembic_upgrade_invokes_subprocess(monkeypatch, tmp_path: Path):
    calls = {}

    def fake_run(cmd, check, capture_output=True, text=True):
        calls["cmd"] = cmd

        class Result:
            stdout = "stdout"
            stderr = ""

        return Result()

    monkeypatch.setattr(migrate_core.subprocess, "run", fake_run)

    cfg = tmp_path / "al.ini"
    result = migrate_core.alembic_upgrade(cfg)

    assert result == {"ok": True, "stdout": "stdout", "stderr": ""}
    assert calls["cmd"] == ["alembic", "-c", str(cfg), "upgrade", "head"]


@pytest.mark.unit
def test_alembic_revision_invokes_subprocess(monkeypatch, tmp_path: Path):
    calls = {}

    def fake_run(cmd, check, capture_output=True, text=True):
        calls["cmd"] = cmd

        class Result:
            stdout = "out"
            stderr = "err"

        return Result()

    monkeypatch.setattr(migrate_core.subprocess, "run", fake_run)

    cfg = tmp_path / "al.ini"
    result = migrate_core.alembic_revision("msg", cfg)

    assert result == {"ok": True, "stdout": "out", "stderr": "err"}
    assert calls["cmd"] == [
        "alembic",
        "-c",
        str(cfg),
        "revision",
        "--autogenerate",
        "-m",
        "msg",
    ]
