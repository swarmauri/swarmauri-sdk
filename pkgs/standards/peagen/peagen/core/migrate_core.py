from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict


# ``alembic.ini`` sits alongside the ``migrations`` directory in the package
# root. ``parents[2]`` reliably resolves to that location for both source and
# installed packages.
ALEMBIC_CFG = Path(__file__).resolve().parents[2] / "alembic.ini"


def alembic_upgrade(cfg: Path = ALEMBIC_CFG) -> Dict[str, Any]:
    """Apply migrations up to HEAD using *cfg*."""
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                str(cfg),
                "upgrade",
                "head",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
    return {"ok": True}


def alembic_downgrade(cfg: Path = ALEMBIC_CFG) -> Dict[str, Any]:
    """Downgrade the database by one revision using *cfg*."""
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                str(cfg),
                "downgrade",
                "-1",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
    return {"ok": True}


def alembic_revision(message: str, cfg: Path = ALEMBIC_CFG) -> Dict[str, Any]:
    """Create a new revision with *message* using *cfg*."""
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                str(cfg),
                "revision",
                "--autogenerate",
                "-m",
                message,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
    return {"ok": True}
