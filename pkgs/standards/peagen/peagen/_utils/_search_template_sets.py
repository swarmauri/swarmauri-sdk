# peagen/_utils/_search_template_sets.py

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from importlib import metadata

import peagen.plugins  # ensures registry is populated
from peagen.plugins import registry 


def get_plugin_template_paths() -> List[Path]:
    """
    Discover directories provided by installed “peagen.template_sets” plugins.

    Each entry-point under the group "peagen.template_sets" corresponds to a module
    or class whose __path__ indicates where its Jinja templates live. We return
    each such directory as a Path, so that Peagen can search for template sets there.
    """
    paths: List[Path] = []
    # registry["template_sets"] maps plugin names to their module/class
    for obj in registry["template_sets"].values():
        # If plugin is a module, use its __path__
        if hasattr(obj, "__path__"):
            for entry in obj.__path__:
                paths.append(Path(entry).resolve())
        # If plugin is a class, inspect its module’s __path__
        else:
            mod = __import__(obj.__module__, fromlist=["__path__"])
            if hasattr(mod, "__path__"):
                for entry in mod.__path__:
                    paths.append(Path(entry).resolve())
    return paths


def build_global_template_search_paths(
    workspace_root: Optional[Path],
    source_packages: List[Dict[str, Any]],
    base_dir: Path,
) -> List[Path]:
    """
    Assemble the global Jinja search path before any package-specific rendering.

    These directories are used to locate template sets by name (e.g., “default”,
    or plugin-provided sets). The order is:

      1. workspace_root (if provided)
         - Ensures that freshly generated files can be included at runtime.
      2. Built-in Peagen templates
         - All paths under peagen.templates.__path__; these contain stock sets.
      3. Plugin template directories
         - Discovered via get_plugin_template_paths(), letting third parties override built-ins.
      4. workspace_root / source_package["dest"] for each source package
         - Makes materialized packages available for Jinja includes.
      5. base_dir (current working directory)
         - Fallback to the project root for any local Jinja files.

    Parameters
    ----------
    workspace_root : Optional[Path]
        Path to the temporary workspace directory.
    source_packages : List[Dict[str, Any]]
        Each dict must have a "dest" key pointing to a subfolder under workspace_root.
    base_dir : Path
        The current working directory (project root).

    Returns
    -------
    List[Path]
        Ordered list of directories for Jinja’s `templates_dir`, to be used
        when locating a template set by name.
    """
    search_paths: List[Path] = []

    # 1) workspace_root
    if workspace_root is not None:
        search_paths.append(workspace_root.resolve())

    # 2) Built-in Peagen templates
    import peagen.template_sets  # noqa: F401
    for entry in peagen.template_sets.__path__:
        search_paths.append(Path(entry).resolve())

    # 3) Plugin template directories
    for plugin_path in get_plugin_template_paths():
        search_paths.append(plugin_path)

    # 4) workspace_root / source_package["dest"]
    if workspace_root is not None:
        for spec in source_packages:
            dest = spec.get("dest")
            if dest:
                search_paths.append((workspace_root / dest).resolve())

    # 5) base_dir (CWD)
    search_paths.append(base_dir.resolve())

    return search_paths


def build_ptree_template_search_paths(
    package_template_dir: Path,
    base_dir: Path,
    workspace_root: Optional[Path],
    source_packages: List[Dict[str, Any]],
) -> List[Path]:
    """
    Assemble the Jinja search path for rendering a single package’s ptree.yaml.j2.

    This function is called immediately after locating `package_template_dir` (i.e.
    the directory for a specific template set). It replaces any global search path
    with a focused list:

      1. package_template_dir
         - Ensures that ptree.yaml.j2 and its includes come from this package’s templates.
      2. base_dir (current working directory)
         - Allows any project-level Jinja files to be included.
      3. workspace_root / source_package["dest"] (for each source package)
         - Makes external packages available for includes.

    All built-ins, plugins, and the old workspace_root at index 0 are discarded here.

    Parameters
    ----------
    package_template_dir : Path
        The directory on disk containing the chosen template set for this package.
    base_dir : Path
        The current working directory (project root).
    workspace_root : Optional[Path]
        Path to the scratch workspace directory.
    source_packages : List[Dict[str, Any]]
        Each dict must have a "dest" key pointing to a subfolder under workspace_root.

    Returns
    -------
    List[Path]
        Ordered list of directories for Jinja’s `templates_dir` when rendering ptree.yaml.j2.
    """
    ptree_paths: List[Path] = []

    # 1) package_template_dir
    ptree_paths.append(package_template_dir.resolve())

    # 2) base_dir (CWD)
    ptree_paths.append(base_dir.resolve())

    # 3) workspace_root / source_package["dest"]
    if workspace_root is not None:
        for spec in source_packages:
            dest = spec.get("dest")
            if dest:
                ptree_paths.append((workspace_root / dest).resolve())

    return ptree_paths


def build_file_template_search_paths(
    record_template_dir: Path,
    workspace_root: Path,
    ptree_search_paths: List[Path],
) -> List[Path]:
    """
    Assemble the Jinja search path for rendering a single file (COPY or GENERATE).

    This function is used inside the file-processing loop, after ptree.yaml.j2 has
    been rendered. We start from `ptree_search_paths` (which was built by
    `build_ptree_template_search_paths`) and then:

      1. Prepend record_template_dir
         - Highest priority: the same directory from which ptree.yaml.j2 was loaded
           (guaranteed to contain any file-level templates).
      2. Prepend workspace_root
         - Ensures that any files generated so far can be `{% include %}`d.
      3. Append the remaining entries from ptree_search_paths[1:]
         - That is:
           a. base_dir (CWD),
           b. workspace_root/source_pkg_dest…

    Parameters
    ----------
    record_template_dir : Path
        Directory of the template set for this file, stored in rec["TEMPLATE_SET"].
    workspace_root : Path
        Path to the scratch workspace directory.
    ptree_search_paths : List[Path]
        List returned by build_ptree_template_search_paths for the current package.
        Its index 0 matches record_template_dir; indices 1… are base_dir, source_packages, etc.

    Returns
    -------
    List[Path]
        Ordered list of directories for Jinja’s `templates_dir` when rendering
        this file’s template.
    """
    # Drop the first element from ptree_search_paths (already re-inserted below)
    fallback = ptree_search_paths[1:]

    file_paths: List[Path] = [
        record_template_dir.resolve(),  # (C1) record-specific templates
        workspace_root.resolve(),       # (C2) workspace so generated files can be included
        *[p.resolve() for p in fallback]  # (C3) base_dir, source_package_dest
    ]
    return file_paths
