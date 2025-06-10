import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.unit
def test_alembic_upgrade_and_current(tmp_path):
    ALEMBIC_CFG = Path(__file__).resolve().parents[2] / "alembic.ini"

    env = os.environ.copy()
    env.setdefault("REDIS_URL", "redis://localhost:6379/0")

    subprocess.run(
        [
            "alembic",
            "-c",
            str(ALEMBIC_CFG),
            "upgrade",
            "head",
        ],
        check=True,
        env=env,
    )

    result = subprocess.run(
        ["alembic", "-c", str(ALEMBIC_CFG), "current"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip()
