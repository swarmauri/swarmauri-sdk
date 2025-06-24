from __future__ import annotations

import importlib.metadata as im
from importlib import import_module
import subprocess
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional

import peagen.template_sets as _pt
from peagen.plugins import registry
from peagen.plugin_manager import resolve_plugin_spec


def _namespace_dirs() -> List[Path]:
    """Return the search roots that may contain template-set folders."""
    return [Path(p) for p in _pt.__path__]


def discover_template_sets() -> Dict[str, List[Path]]:
    """Return mapping ``set_name -> [locations...]``."""
    sets: Dict[str, List[Path]] = {}
    for ns_root in _namespace_dirs():
        try:
            for child in ns_root.iterdir():
                if child.is_dir():
                    sets.setdefault(child.name, []).append(child)
        except PermissionError:
            continue
    for name, plugin in registry.get("template_sets", {}).items():
        mod = resolve_plugin_spec("template_sets", name)
        module = mod if isinstance(mod, ModuleType) else import_module(mod.__module__)
        if hasattr(module, "__path__"):
            for root in module.__path__:
                sets.setdefault(name, []).append(Path(root))
        elif hasattr(module, "__file__"):
            sets.setdefault(name, []).append(Path(module.__file__).parent)
    return sets


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def list_template_sets() -> Dict[str, Any]:
    """Return information about all discovered template sets."""
    discovered = discover_template_sets()
    result = {"total": len(discovered), "sets": []}
    for name, paths in sorted(discovered.items()):
        entry: Dict[str, Any] = {"name": name, "paths": [str(p) for p in paths]}
        result["sets"].append(entry)
    return result


# ---------------------------------------------------------------------------
# Show
# ---------------------------------------------------------------------------


def show_template_set(name: str) -> Dict[str, Any]:
    """Return detailed info for one template set."""
    discovered = discover_template_sets()
    if name not in discovered:
        raise ValueError(f"Template-set '{name}' not found")

    primary = discovered[name][0]
    info: Dict[str, Any] = {"name": name, "location": str(primary)}
    if len(discovered[name]) > 1:
        info["other_locations"] = [str(p) for p in discovered[name][1:]]

    def _iter_files(base: Path):
        for fp in base.rglob("*"):
            if fp.is_file():
                yield str(fp.relative_to(base))

    info["files"] = list(_iter_files(primary))
    return info


# ---------------------------------------------------------------------------
# Add
# ---------------------------------------------------------------------------


def add_template_set(
    source: str,
    *,
    from_bundle: Optional[str] = None,
    editable: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """Install a template-set distribution."""
    src_path = Path(from_bundle) if from_bundle else Path(source)
    is_local = src_path.exists()

    def _build_installer(use_editable: bool) -> List[str]:
        if shutil.which("uv"):
            base = ["uv", "pip", "install"]
        else:
            base = [sys.executable, "-m", "pip", "install"]
        base += ["--no-deps"]
        if force:
            base += ["--upgrade", "--force-reinstall"]
        if use_editable:
            base += ["-e"]
        return base

    if is_local:
        if src_path.is_dir():
            pip_cmd = _build_installer(editable)
            pip_cmd.append(str(src_path.resolve()))
        else:
            pip_cmd = _build_installer(False)
            pip_cmd.append(str(src_path.resolve()))
    else:
        pip_cmd = _build_installer(False)
        pip_cmd.append(source)

    sets_before = set(discover_template_sets().keys())
    try:
        subprocess.run(
            pip_cmd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        from peagen.errors import TemplateSetInstallError

        raise TemplateSetInstallError(
            source, exc.stdout or "installation failed"
        ) from exc

    sets_after = set(discover_template_sets().keys())
    new_sets = sorted(sets_after - sets_before)
    return {"installed": new_sets}


# ---------------------------------------------------------------------------
# Remove
# ---------------------------------------------------------------------------


def remove_template_set(
    name: str,
) -> Dict[str, Any]:
    """Uninstall the package that exposes *name* as a template-set."""
    dists: List[str] = []
    for dist in im.distributions():
        if any(
            ep.group == "peagen.template_sets" and ep.name == name
            for ep in dist.entry_points
        ):
            dists.append(dist.metadata["Name"])

    if not dists:
        raise ValueError(f"Template-set '{name}' not found")

    PROTECTED_DISTS = {"peagen"}
    removable = [d for d in dists if d.lower() not in PROTECTED_DISTS]
    if not removable:
        raise ValueError("Cannot uninstall bundled template-set")
    dists = removable

    if shutil.which("uv"):
        cmd = ["uv", "pip", "uninstall"] + dists
    else:
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y"] + dists

    try:
        subprocess.run(
            cmd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        from peagen.errors import TemplateSetUninstallError

        raise TemplateSetUninstallError(
            dists, exc.stdout or "uninstall failed"
        ) from exc

    remaining = discover_template_sets()
    return {"removed": name not in remaining, "dists": dists}
