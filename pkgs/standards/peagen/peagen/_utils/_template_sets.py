"""Install template-set packages specified in .peagen.toml."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, List

from peagen.plugin_manager import resolve_plugin_spec
from jinja2 import FileSystemLoader
from peagen.plugins import registry


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
    """Install each template-set spec and return metadata."""
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
            from peagen.errors import TemplateSetInstallError

            raise TemplateSetInstallError(name, str(exc)) from exc
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


# --------------------------------------------------------------------------- #
# Helper – locate a template-set folder on the current Jinja search-path      #
# --------------------------------------------------------------------------- #
def _locate_template_set(template_set: str, loader: FileSystemLoader) -> Path:
    """
    Resolve *template_set* to a concrete directory, trying in this order:

    1.  Absolute folder path passed by the caller.
    2.  ``<base>/<template_set>`` under every directory in ``loader.searchpath``.
    3.  A plugin registered in ``peagen.plugins.registry["template_sets"]`` whose
        *entry-point name* matches *template_set*.

    Returns
    -------
    pathlib.Path  (absolute, resolved)

    Raises
    ------
    ValueError  if no matching directory can be found.
    """

    # ------------------------------------------------------------------ #
    # 1) Absolute path given directly                                    #
    # ------------------------------------------------------------------ #
    cand = Path(template_set)
    if cand.is_absolute() and cand.is_dir():
        return cand.resolve()

    # ------------------------------------------------------------------ #
    # 2) walk the Jinja2 loader search path                              #
    # ------------------------------------------------------------------ #
    for base in loader.searchpath:
        candidate = Path(base) / template_set
        if candidate.is_dir():
            return candidate.resolve()

    # ------------------------------------------------------------------ #
    # 3) fallback to plugin registry                                     #
    # ------------------------------------------------------------------ #
    plugin = registry.get("template_sets", {}).get(template_set)
    if plugin is not None:
        target = resolve_plugin_spec("template_sets", template_set)
        target_mod: ModuleType
        if isinstance(target, ModuleType):
            target_mod = target
        else:  # class
            target_mod = import_module(target.__module__)

        # Prefer module.__path__[0] (packages) then module.__file__.
        if hasattr(target_mod, "__path__"):  # namespace / pkg
            dir_path = Path(next(iter(target_mod.__path__))).resolve()
            if dir_path.is_dir():
                return dir_path
        if hasattr(target_mod, "__file__"):  # single-file module
            dir_path = Path(target_mod.__file__).parent.resolve()
            if dir_path.is_dir():
                return dir_path

    # ------------------------------------------------------------------ #
    # Nothing matched → fail                                              #
    # ------------------------------------------------------------------ #
    raise ValueError(
        f"Template set '{template_set}' not found in "
        f"loader.searchpath or plugin registry. "
        f"Search path = {', '.join(str(p) for p in loader.searchpath)}"
    )
