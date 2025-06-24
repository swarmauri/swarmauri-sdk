"""
peagen.core.sort_core
=====================

Project-agnostic “sort” logic for Peagen v2.

Public API
----------
- _merge_cli_into_toml()
- sort_single_project()
- sort_all_projects()
- sort_file_records()

Internal helpers (prefixed “_”) are intentionally *not* exported.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from jinja2 import Environment

from peagen._utils._graph import _topological_sort, _transitive_dependency_sort
from peagen._utils._jinja import _build_jinja_env
from peagen._utils._template_sets import _locate_template_set


# --------------------------------------------------------------------------- #
# 1) Public façade – single-project                                           #
# --------------------------------------------------------------------------- #
def sort_single_project(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    params comes straight from _utils.config_loader.resolve_cfg().
    Returns  {"sorted": [ "0) file_a", "1) file_b", … ]}  or  {"error": "..."}.
    """
    try:
        proj_name: str | None = params["project_name"]
        if proj_name is None:
            return {"error": "project_name is required for single-project sort."}

        # --- obtain YAML text -----------------------------------------------------
        data_src = params["projects_payload"]

        # If it *looks* like an existing file path, read it; otherwise treat
        # the value itself as the YAML document.
        try:
            maybe_path = Path(data_src)
            if maybe_path.is_file():
                yaml_data = maybe_path.read_text()
            else:
                yaml_data = data_src
        except (OSError, TypeError):  # not a valid path
            yaml_data = data_src

        yaml_data = yaml.safe_load(yaml_data)
        projects_list: List[Dict[str, Any]] = (
            yaml_data.get("PROJECTS") if isinstance(yaml_data, dict) else yaml_data
        )

        project_spec = next(
            (p for p in projects_list if p.get("NAME") == proj_name), None
        )
        if project_spec is None:
            return {"error": f"Project '{proj_name}' not found in {data_src!s}"}

        # --- run the actual sort --------------------------------------------------
        sorted_recs, next_idx = _run_sort(
            project=project_spec,
            cfg=params["cfg"],
            start_idx=params["start_idx"],
            start_file=params["start_file"],
            transitive=params["transitive"],
        )
        # --- pretty-print list ----------------------------------------------------
        show_deps = params["show_dependencies"]
        base_idx: int = params.get("start_idx", 0) or 0
        lines: List[str] = []
        for i, rec in enumerate(sorted_recs):
            idx = i + base_idx
            name = rec["RENDERED_FILE_NAME"]
            if show_deps:
                deps = _get_immediate_dependencies(sorted_recs, name)
                lines.append(
                    f"{idx}) {name}   (deps: {', '.join(deps) if deps else 'None'})"
                )
            else:
                lines.append(f"{idx}) {name}")
        return {"sorted": lines}

    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


# --------------------------------------------------------------------------- #
# 2) Public façade – all projects                                             #
# --------------------------------------------------------------------------- #
def sort_all_projects(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Iterate all projects in the payload, returning:
        {"sorted_all_projects": { "ProjA": [...], "ProjB": [...] }}
    On a per-project failure we embed the error string in place of the list so
    that one bad project doesn’t fail the whole command.
    """
    try:
        # If it *looks* like an existing file path, read it; otherwise treat
        # the value itself as the YAML document.
        data_src = params["projects_payload"]
        try:
            maybe_path = Path(data_src)
            if maybe_path.is_file():
                yaml_text = maybe_path.read_text()
            else:
                yaml_text = data_src
        except (OSError, TypeError):  # not a valid path
            yaml_text = data_src

        yaml_data = yaml.safe_load(yaml_text)
        projects_list: List[Dict[str, Any]] = (
            yaml_data.get("PROJECTS") if isinstance(yaml_data, dict) else yaml_data
        )

        out: Dict[str, List[str]] = {}
        for proj in projects_list:
            name = proj.get("NAME", "<unnamed>")
            local_params = {**params, "project_name": name}
            result = sort_single_project(local_params)
            out[name] = result.get("sorted") or [
                f"ERROR: {result.get('error', 'unknown')}"
            ]

        return {"sorted_all_projects": out}

    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


# --------------------------------------------------------------------------- #
# 3) Core engine – gather records → delegate to sort_file_records             #
# --------------------------------------------------------------------------- #
def _run_sort(
    *,
    project: Dict[str, Any],
    cfg: Dict[str, Any],
    start_idx: int,
    start_file: str | None,
    transitive: bool,
) -> Tuple[List[Dict[str, Any]], int]:
    # 3-A) Build a legacy-compatible Jinja2 env that already includes
    #      built-ins, plugin template-sets, workspace dir, etc.

    j2_env = _build_jinja_env(cfg, workspace_root=cfg.get("workspace_root"))
    # 3-B) Collect raw file_records from the project spec
    file_records = _collect_file_records(project, j2_env)
    # 3-C) Finally, get the right order
    sorted_records, next_idx = sort_file_records(
        file_records=file_records,
        start_idx=start_idx,
        start_file=start_file,
        transitive=transitive,
    )
    return sorted_records, next_idx


# --------------------------------------------------------------------------- #
# 4) Helper – turn FILES entries into canonical records                       #
# --------------------------------------------------------------------------- #
def _collect_file_records(project: dict, jinja_env: Environment):
    out: list[dict] = []

    # 1) fast-path – existing behaviour for hand-written FILES arrays
    if project.get("FILES"):
        out.extend(_collect_file_records_from_files(project, jinja_env))

    # 2) fall-back – iterate PACKAGES and render ptree.yaml.j2 like the legacy flow
    for pkg in project.get("PACKAGES", []):
        template_set = (
            pkg.get("TEMPLATE_SET_OVERRIDE")
            or pkg.get("TEMPLATE_SET")
            or project.get("TEMPLATE_SET", "default")
        )
        template_dir = _locate_template_set(template_set, jinja_env.loader)
        ptree = Path(template_dir) / "ptree.yaml.j2"
        if not ptree.exists():
            continue

        ctx = {"PROJ": project | {"PKGS": [pkg]}}
        rendered = jinja_env.from_string(ptree.read_text()).render(ctx)
        partial = yaml.safe_load(rendered)
        records = partial["FILES"] if isinstance(partial, dict) else partial
        for r in records:
            r["TEMPLATE_SET"] = str(template_dir)
        out.extend(records)

    if not out:
        raise ValueError(
            f"No file records could be extracted from project '{project.get('NAME')}'."
        )
    return out


# ------------------------------------------------------------------- #
# Legacy helper – lift raw FILES entries into canonical records       #
# ------------------------------------------------------------------- #
def _collect_file_records_from_files(
    project: dict, jinja_env: Environment
) -> list[dict]:
    """
    The old Peagen accepted a literal FILES: [ … ] block at the root of a
    project entry.  We keep that path for backwards-compat.

    • It copies the list verbatim,
    • injects TEMPLATE_SET so downstream renders can still locate it.
    """
    template_set = project.get("TEMPLATE_SET", "default")
    try:
        tpl_dir = _locate_template_set(template_set, jinja_env.loader)
    except ValueError:  # handwritten files may live outside any set
        tpl_dir = Path(".")  # still supply *something* non-empty

    out = []
    for rec in project["FILES"]:
        rec = rec.copy()  # never mutate caller’s dict
        rec.setdefault("TEMPLATE_SET", str(tpl_dir))
        out.append(rec)
    return out


# --------------------------------------------------------------------------- #
# 5) Immediate-dependency helper (unchanged)                                  #
# --------------------------------------------------------------------------- #
def _get_immediate_dependencies(
    sorted_records: List[Dict[str, Any]], file_name: str
) -> List[str]:
    deps: List[str] = []
    for rec in sorted_records:
        if file_name in rec.get("EXTRAS", {}).get("DEPENDENCIES", []):
            deps.append(rec["RENDERED_FILE_NAME"])
    return deps


# --------------------------------------------------------------------------- #
# 6) Sorting primitive – exposed for tests / other modules                    #
# --------------------------------------------------------------------------- #
def sort_file_records(
    *,
    file_records: List[Dict[str, Any]],
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Core ordering algorithm shared by both CLI & worker code paths.

    Parameters
    ----------
    file_records   : canonical list from _collect_file_records()
    start_idx      : numerical skip count
    start_file     : name to resume from (ignored if transitive=True)
    transitive     : if True, keep only the transitive closure up to start_file

    Returns
    -------
    (sorted_records, next_index_after_last_processed)
    """

    # -- choose algorithm ----------------------------------------------------
    try:
        if transitive and start_file:
            sorted_records = _transitive_dependency_sort(file_records, start_file)
        else:
            sorted_records = _topological_sort(file_records)
    except Exception as exc:  # noqa: BLE001
        from peagen.errors import DependencySortError

        raise DependencySortError(str(exc)) from exc

    # -- apply positional skipping ------------------------------------------
    if start_file and not transitive:
        try:
            skip = next(
                i
                for i, rec in enumerate(sorted_records)
                if rec["RENDERED_FILE_NAME"] == start_file
            )
            sorted_records = sorted_records[skip:]
        except StopIteration:
            pass

    if start_idx > 0:
        sorted_records = sorted_records[start_idx:]

    next_index = start_idx + len(sorted_records)
    return sorted_records, next_index
