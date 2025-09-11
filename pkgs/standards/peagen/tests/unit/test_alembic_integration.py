import os
import sqlite3
import subprocess
from pathlib import Path
from peagen.core.migrate_core import ALEMBIC_CFG

import pytest


@pytest.mark.unit
def test_alembic_upgrade_and_current(tmp_path):
    alembic_ini = ALEMBIC_CFG
    repo_root = Path(__file__).resolve().parents[5]

    env = os.environ.copy()
    env.pop("PG_HOST", None)
    env.pop("PG_PORT", None)
    env.pop("PG_DB", None)
    env.pop("PG_USER", None)
    env.pop("PG_PASS", None)
    env.pop("PG_DSN", None)

    db_path = repo_root / "gateway.db"
    if db_path.exists():
        db_path.unlink()

    subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini),
            "upgrade",
            "heads",
        ],
        check=True,
        cwd=repo_root,
        env=env,
    )

    subprocess.run(
        ["alembic", "-c", str(alembic_ini), "current"],
        check=True,
        cwd=repo_root,
        env=env,
    )

    # Ensure tables exist since migrations are empty
    from sqlalchemy.ext.asyncio import create_async_engine
    import asyncio
    from peagen.orm import Base

    async def init_db() -> None:
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            execution_options={"schema_translate_map": {"peagen": None}},
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(init_db())

    db_path = repo_root / "gateway.db"
    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='works'"
        )
        assert cur.fetchone() is not None
        conn.execute("PRAGMA table_info(works)")
