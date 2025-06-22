import os
import sqlite3
import subprocess
from pathlib import Path

import pytest


@pytest.mark.unit
def test_alembic_upgrade_and_current(tmp_path):
    alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
    repo_root = Path(__file__).resolve().parents[5]

    env = os.environ.copy()
    env.setdefault("REDIS_URL", "redis://localhost:6379/0")
    env.pop("PG_HOST", None)
    env.pop("PG_PORT", None)
    env.pop("PG_DB", None)
    env.pop("PG_USER", None)
    env.pop("PG_PASS", None)

    subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini),
            "upgrade",
            "head",
        ],
        check=True,
        cwd=repo_root,
        env=env,
    )

    result = subprocess.run(
        ["alembic", "-c", str(alembic_ini), "current"],
        check=True,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip()

    db_path = repo_root / "gateway.db"
    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='task_runs'"
        )
        assert cur.fetchone() is not None
        cur = conn.execute("PRAGMA table_info(task_runs)")
        cols = {row[1] for row in cur.fetchall()}
        assert "commit_hexsha" in cols
        assert "oids" in cols
