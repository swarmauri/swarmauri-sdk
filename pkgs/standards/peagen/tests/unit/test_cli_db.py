import pytest
from typer.testing import CliRunner

from peagen.cli import app
from peagen.cli.commands import db as db_mod


@pytest.mark.unit
def test_local_db_upgrade_prints_output(monkeypatch):
    async def fake_handler(task):
        return {"ok": True, "stdout": "OUT", "stderr": "ERR"}

    monkeypatch.setattr(db_mod, "migrate_handler", fake_handler)
    runner = CliRunner()
    result = runner.invoke(app, ["local", "db", "upgrade"])

    assert result.exit_code == 0
    assert "OUT" in result.output
    assert "ERR" in result.output
