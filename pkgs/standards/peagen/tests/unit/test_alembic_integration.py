import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.unit
def test_alembic_upgrade_and_current(tmp_path):
    repo_root = Path(__file__).resolve().parents[5]
    alembic_ini = repo_root / "pkgs/standards/peagen/alembic.ini"

    env = os.environ.copy()
    env.setdefault("REDIS_URL", "redis://localhost:6379/0")

    subprocess.run([
        "alembic",
        "-c",
        str(alembic_ini),
        "upgrade",
        "head",
    ], check=True, cwd=repo_root, env=env)

    result = subprocess.run(
        ["alembic", "-c", str(alembic_ini), "current"],
        check=True,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip()
