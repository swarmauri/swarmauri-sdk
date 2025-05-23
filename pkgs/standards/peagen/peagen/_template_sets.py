"""Install template-set packages specified in .peagen.toml."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


def _build_pip_cmd(editable: bool = False) -> List[str]:
    """Return a pip install command, preferring uv if available."""
    if shutil.which("uv"):
        cmd = ["uv", "pip", "install", "--no-deps"]
    else:
        cmd = [sys.executable, "-m", "pip", "install", "--no-deps"]
    if editable:
        cmd.append("-e")
    return cmd


def _pip_install(path: str, editable: bool = False) -> None:
    cmd = _build_pip_cmd(editable)
    cmd.append(path)
    subprocess.check_call(cmd)


def install_template_sets(specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Install each template-set spec and return manifest info."""
    installed: List[Dict[str, Any]] = []
    tmp_root = Path(tempfile.mkdtemp(prefix="tmplset_"))
    for spec in specs:
        typ = spec.get("type")
        target = spec.get("target")
        name = spec.get("name")
        try:
            if typ == "pip":
                _pip_install(target)
            elif typ == "git":
                clone_dir = tmp_root / name
                cmd = ["git", "clone", "--depth", "1"]
                if spec.get("ref"):
                    cmd += ["--branch", spec["ref"]]
                cmd += [target, str(clone_dir)]
                subprocess.check_call(cmd)
                _pip_install(str(clone_dir))
            elif typ == "local":
                _pip_install(target, editable=True)
            elif typ == "bundle":
                _pip_install(target)
            else:
                raise ValueError(f"unknown template-set type: {typ}")
        except Exception as exc:
            raise RuntimeError(f"failed to install template-set {name}: {exc}") from exc
        # try to resolve installed version
        version = "unknown"
        try:
            from importlib.metadata import version as _ver

            version = _ver(name)
        except Exception:
            pass
        installed.append(
            {
                "name": name,
                "type": typ,
                "version": version,
                "source": target,
            }
        )
    shutil.rmtree(tmp_root, ignore_errors=True)
    return installed
