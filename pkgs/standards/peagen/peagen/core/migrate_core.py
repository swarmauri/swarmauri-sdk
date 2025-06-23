from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List


# ``alembic.ini`` sits alongside the ``migrations`` directory in the package
# root. When running from source this lives two levels up from this file, while
# an installed wheel places it one level up. Check both locations for
# robustness.
_src_cfg = Path(__file__).resolve().parents[2] / "alembic.ini"
_pkg_cfg = Path(__file__).resolve().parents[1] / "alembic.ini"
ALEMBIC_CFG = _src_cfg if _src_cfg.exists() else _pkg_cfg


def _run_alembic(cmd: List[str], stream: bool) -> Dict[str, Any]:
    """Run *cmd* returning ``stdout`` and ``stderr``.

    If *stream* is ``True``, forward output to the parent process while
    capturing it.
    """
    if stream:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        stdout_lines: List[str] = []
        stderr_lines: List[str] = []

        def _pump(src, dest_stream, buffer):
            for line in iter(src.readline, ""):
                dest_stream.write(line)
                dest_stream.flush()
                buffer.append(line)
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
            "error": f"exit code {proc.returncode}",
            "stdout": stdout,
            "stderr": stderr,
        }

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": str(exc),
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }
    return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}


def alembic_upgrade(cfg: Path = ALEMBIC_CFG, *, stream: bool = False) -> Dict[str, Any]:
    """Apply migrations up to HEAD using *cfg*."""
    return _run_alembic(
        [
            "alembic",
            "-c",
            str(cfg),
            "upgrade",
            "head",
        ],
        stream,
    )


def alembic_downgrade(
    cfg: Path = ALEMBIC_CFG, *, stream: bool = False
) -> Dict[str, Any]:
    """Downgrade the database by one revision using *cfg*."""
    return _run_alembic(
        [
            "alembic",
            "-c",
            str(cfg),
            "downgrade",
            "-1",
        ],
        stream,
    )


def alembic_revision(
    message: str, cfg: Path = ALEMBIC_CFG, *, stream: bool = False
) -> Dict[str, Any]:
    """Create a new revision with *message* using *cfg*."""
    return _run_alembic(
        [
            "alembic",
            "-c",
            str(cfg),
            "revision",
            "--autogenerate",
            "-m",
            message,
        ],
        stream,
    )
