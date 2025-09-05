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
    assert calls["cmd"] == ["alembic", "-c", str(cfg), "upgrade", "heads"]


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


@pytest.mark.unit
def test_alembic_upgrade_stream(monkeypatch, tmp_path: Path):
    calls = {}

    class FakeStream:
        def __init__(self, lines):
            self._lines = iter(lines)

        def readline(self):
            try:
                return next(self._lines)
            except StopIteration:
                return ""

        def close(self):
            pass

    class FakeProc:
        def __init__(self):
            self.stdout = FakeStream(["out\n", ""])
            self.stderr = FakeStream(["err\n", ""])
            self.returncode = 0

        def wait(self):
            return 0

    def fake_popen(cmd, stdout, stderr, text, bufsize):
        calls["cmd"] = cmd
        return FakeProc()

    monkeypatch.setattr(migrate_core.subprocess, "Popen", fake_popen)

    cfg = tmp_path / "al.ini"
    result = migrate_core.alembic_upgrade(cfg, stream=True)

    assert result == {"ok": True, "stdout": "out\n", "stderr": "err\n"}
    assert calls["cmd"] == ["alembic", "-c", str(cfg), "upgrade", "heads"]
