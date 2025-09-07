"""Ensure only a single SQLite database file is created on startup."""

from importlib import reload
from pathlib import Path

import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sqlite_single_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from auto_authn import db as db_module
    from auto_authn import app as app_module

    reload(db_module)
    reload(app_module)

    await app_module._startup()

    files = {p.name for p in Path(tmp_path).iterdir()}
    assert "authn__authn.db" in files
    assert "authn.db" not in files
