"""
peagen._utils._search_template_sets
===================================
Utilities for assembling Jinja2 *template search paths*.

All legacy notions of ``workspace_root`` and ``source_packages`` have been
removed.  The search-path logic is now entirely filesystem-static:

Global look-ups
---------------
    * built-in Peagen template sets
    * template directories exposed by *peagen.template_sets* plugins
    * the caller-supplied **base_dir** (usually CWD)

Package-level (ptree.yaml.j2) rendering
---------------------------------------
    * <package_template_dir>
    * base_dir

File-level rendering
--------------------
    * <record_template_dir>
    * all entries from *ptree_search_paths* (i.e., base_dir)

This simplifies reasoning and avoids any dependence on transient workspaces.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import peagen.plugins  # noqa: F401 – populate registry
from peagen.plugins import registry


# ───────────────────────── plugin discovery ──────────────────────────────
def get_plugin_template_paths() -> List[Path]:
    """Return directories contributed by “peagen.template_sets” plugins."""
    paths: List[Path] = []
    for obj in registry["template_sets"].values():
        if hasattr(obj, "__path__"):  # module
            for entry in obj.__path__:
                paths.append(Path(entry).resolve())
        else:  # class – inspect its defining module
            mod = __import__(obj.__module__, fromlist=["__path__"])
            if hasattr(mod, "__path__"):
                for entry in mod.__path__:
                    paths.append(Path(entry).resolve())
    return paths


# ─────────────────────── global search paths ────────────────────────────
def build_global_template_search_paths(base_dir: Path) -> List[Path]:
    """
    Compute the global Jinja search path used when locating template *sets*.

    Order:
      1. Built-in Peagen template directories
      2. Plugin-provided template directories
      3. base_dir (typically the project root)
    """
    search_paths: List[Path] = []

    # 1) built-in templates
    import peagen.template_sets  # noqa: F401
    for entry in peagen.template_sets.__path__:
        search_paths.append(Path(entry).resolve())

    # 2) plugin templates
    search_paths.extend(get_plugin_template_paths())

    # 3) caller-supplied base_dir
    search_paths.append(base_dir.resolve())

    return search_paths


# ─────────────────── ptree-level search paths ────────────────────────────
def build_ptree_template_search_paths(
    package_template_dir: Path,
    base_dir: Path,
) -> List[Path]:
    """
    Search path for rendering an individual package’s *ptree.yaml.j2* file.

    Order:
      1. package_template_dir
      2. base_dir
    """
    return [package_template_dir.resolve(), base_dir.resolve()]


# ─────────────────── file-level search paths ─────────────────────────────
def build_file_template_search_paths(
    record_template_dir: Path,
    ptree_search_paths: List[Path],
) -> List[Path]:
    """
    Search path for rendering a *single file* inside a package.

    Order:
      1. record_template_dir  (highest priority)
      2. all entries from ptree_search_paths (package_template_dir, base_dir)
    """
    return [record_template_dir.resolve(), *[p.resolve() for p in ptree_search_paths]]
