"""
peagen.core.migrate_core
────────────────────────
Small wrapper around Alembic that

* finds the packaged ``alembic.ini`` automatically,
* allows the caller to inject the live PG_DSN (Postgres, MySQL, …),
* streams or captures stdout/stderr,
* returns a simple dict → {"ok": bool, "stdout": str, "stderr": str, "error": str | None}.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

# --------------------------------------------------------------------------- #
# Locate alembic.ini – works from source checkouts *and* installed wheels
# --------------------------------------------------------------------------- #
_src_cfg = Path(__file__).resolve().parents[2] / "alembic.ini"
_pkg_cfg = Path(__file__).resolve().parents[1] / "alembic.ini"
ALEMBIC_CFG: Path = _src_cfg if _src_cfg.exists() else _pkg_cfg


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _run_alembic(
    cmd: List[str],
    stream: bool = False,
    *,
    env: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Execute *cmd* in a subprocess.

    If *stream* is True, stdout/stderr are shown live **and** collected;
    otherwise they are only collected.

    Returns
    -------
    dict
        ``{"ok": bool, "stdout": str, "stderr": str, "error": str | None}``
    """
    if stream:
        popen_kwargs: Dict[str, Any] = {}
        if env is not None:
            popen_kwargs["env"] = env
        proc = subprocess.Popen(  # noqa: S603
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            **popen_kwargs,
        )

        stdout_lines: List[str] = []
        stderr_lines: List[str] = []

        def _pump(src, dest, buf):
            for line in iter(src.readline, ""):
                dest.write(line)
                dest.flush()
                buf.append(line)
            src.close()

        threads = [
            threading.Thread(
                target=_pump, args=(proc.stdout, sys.stdout, stdout_lines)
            ),
            threading.Thread(
                target=_pump, args=(proc.stderr, sys.stderr, stderr_lines)
            ),
        ]
        for t in threads:
            t.start()

        proc.wait()
        for t in threads:
            t.join()

        stdout = "".join(stdout_lines)
        stderr = "".join(stderr_lines)

        if proc.returncode == 0:
            return {"ok": True, "stdout": stdout, "stderr": stderr}
        return {
            "ok": False,
            "stdout": stdout,
            "stderr": stderr,
            "error": f"exit code {proc.returncode}",
        }

    # ------- capture-only branch ------------------------------------------
    try:
        run_kwargs: Dict[str, Any] = {}
        if env is not None:
            run_kwargs["env"] = env
        res = subprocess.run(  # noqa: S603,S607
            cmd,
            check=True,
            capture_output=True,
            text=True,
            **run_kwargs,
        )
        return {"ok": True, "stdout": res.stdout, "stderr": res.stderr}
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        return {
            "ok": False,
            "stdout": exc.stdout,
            "stderr": exc.stderr,
            "error": str(exc),
        }


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def alembic_upgrade(
    cfg: Path | str = ALEMBIC_CFG,
    *,
    stream: bool = False,
    db_url: str | None = None,
) -> Dict[str, Any]:
    """Upgrade to *heads* using *cfg*."""
    cmd = ["alembic", "-c", str(cfg), "upgrade", "heads"]
    env = {**os.environ, "PG_DSN": db_url} if db_url else None
    return _run_alembic(cmd, stream, env=env)


def alembic_downgrade(
    cfg: Path | str = ALEMBIC_CFG,
    *,
    stream: bool = False,
    db_url: str | None = None,
) -> Dict[str, Any]:
    """Step down one revision using *cfg*."""
    cmd = ["alembic", "-c", str(cfg), "downgrade", "-1"]
    env = {**os.environ, "PG_DSN": db_url} if db_url else None
    return _run_alembic(cmd, stream, env=env)


def alembic_revision(
    message: str,
    cfg: Path | str = ALEMBIC_CFG,
    *,
    stream: bool = False,
    db_url: str | None = None,
) -> Dict[str, Any]:
    """Autogenerate a new revision with *message*."""
    cmd = ["alembic", "-c", str(cfg), "revision", "--autogenerate", "-m", message]
    env = {**os.environ, "PG_DSN": db_url} if db_url else None
    return _run_alembic(cmd, stream, env=env)
