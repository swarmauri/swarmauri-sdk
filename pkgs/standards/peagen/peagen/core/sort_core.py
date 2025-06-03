# peagen/core/sorter.py

import yaml
from pathlib import Path
from typing import Any, Dict, List, Tuple
from peagen._utils.config_loader import load_peagen_toml
from peagen._utils._graph import _topological_sort, _transitive_dependency_sort

# ----------------------------------------------------------------------------
# Private helper: merge CLI‐only flags into TOML (no more env or plugin overrides)
# ----------------------------------------------------------------------------
def _merge_cli_into_toml(
    *,
    projects_payload: str,
    project_name: str | None,
    start_idx: int | None,
    start_file: str | None,
    verbose: int,
    transitive: bool,
    show_dependencies: bool,
) -> Dict[str, Any]:
    """
    Load .peagen.toml (single source of truth) and merge only these CLI flags:
      - project_name
      - start_idx
      - start_file
      - verbose
      - transitive
      - show_dependencies

    Arguments:
      projects_payload: path to the YAML payload
      project_name:    single project to sort (if any)
      start_idx:       index to start from
      start_file:      file to start from
      verbose:         verbosity level
      transitive:      whether to include transitive dependencies
      show_dependencies: whether to append dependency info
    """
    cfg: Dict[str, Any] = load_peagen_toml(".peagen.toml")

    # Override top‐level flags from CLI
    cfg["transitive"] = transitive
    # (We no longer override plugin_mode, agent_env, etc.)

    return {
        "projects_payload_path": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx or 0,
        "start_file": start_file,
        "verbose": verbose,
        "transitive": transitive,
        "show_dependencies": show_dependencies,
        "cfg": cfg,
    }

# ----------------------------------------------------------------------------
# Public API: sort exactly one project
# ----------------------------------------------------------------------------
def sort_single_project(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sort a single project according to the TOML + CLI overrides.
    Returns { "sorted": [ "0) file_a", "1) file_b", … ] } or { "error": "…" }.
    """
    try:
        proj_name = params["project_name"]
        if proj_name is None:
            return {"error": "project_name is required for single‐project sort."}

        # Load and parse the YAML payload (list of project dicts)
        payload_path = Path(params["projects_payload_path"])
        projects_list = yaml.safe_load(payload_path.read_text())
        project_spec = next((p for p in projects_list if p.get("NAME") == proj_name), None)
        if project_spec is None:
            return {"error": f"Project '{proj_name}' not found in {payload_path!r}"}

        # Delegate to the private sorter
        sorted_recs, next_idx = _run_sort(
            project=project_spec,
            cfg=params["cfg"],
            start_idx=params["start_idx"],
            start_file=params["start_file"],
            verbose=params["verbose"],
            transitive=params["transitive"],
        )

        # Format the output list
        lines: List[str] = []
        for i, rec in enumerate(sorted_recs):
            idx = i + (next_idx or 0)
            fname = rec.get("RENDERED_FILE_NAME")
            if params["show_dependencies"]:
                deps = get_immediate_dependencies(sorted_recs, fname)
                dep_str = ", ".join(deps) if deps else "None"
                lines.append(f"{idx}) {fname}  (deps: {dep_str})")
            else:
                lines.append(f"{idx}) {fname}")
        return {"sorted": lines}

    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------------
# Public API: sort all projects
# ----------------------------------------------------------------------------
def sort_all_projects(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sort every project in the payload. Returns { "sorted_all_projects": { name: [ … ] } }.
    """
    try:
        payload_path = Path(params["projects_payload_path"])
        projects_list = yaml.safe_load(payload_path.read_text())
        result_map: Dict[str, List[str]] = {}

        for proj in projects_list:
            proj_name = proj.get("NAME")
            if not proj_name:
                continue
            local = {**params, "project_name": proj_name}
            out = sort_single_project(local)
            if "error" in out:
                result_map[proj_name] = [f"ERROR: {out['error']}"]
            else:
                result_map[proj_name] = out.get("sorted", [])
        return {"sorted_all_projects": result_map}

    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------------
# Private: actual sorting logic (mirrors old Peagen.process_single_project)
# ----------------------------------------------------------------------------
def _run_sort(
    *,
    project: Dict[str, Any],
    cfg: Dict[str, Any],
    start_idx: int,
    start_file: str | None,
    verbose: int,
    transitive: bool,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Implements the “sorting” algorithm. Returns (list_of_records, next_idx).
    Each record is a dict (e.g. { "RENDERED_FILE_NAME": "...", "EXTRAS": { … } }).
    """

    from jinja2 import Environment, FileSystemLoader

    # (1) Build Jinja2 environment based only on TOML (no CLI‐only dirs)
    search_paths: List[str] = []
    for path_str in cfg.get("template_paths", []):
        search_paths.append(str(Path(path_str)))
    j2_env = Environment(loader=FileSystemLoader(search_paths))

    # (2) Your existing sorting algorithm. Stubbed here:
    def _compute_sort_order(
        project: Dict[str, Any],
        jinja_env: Environment,
        transitive: bool,
        start_idx: int,
        start_file: str | None,
        verbose: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        # … insert real “sort” logic here, respecting transitive & verbose …
        records: List[Dict[str, Any]] = []
        next_idx = 0
        # populate records, next_idx …
        return records, next_idx

    return _compute_sort_order(
        project,
        j2_env,
        transitive=transitive,
        start_idx=start_idx,
        start_file=start_file,
        verbose=verbose,
    )

# ----------------------------------------------------------------------------
# Private: compute immediate dependencies (unchanged)
# ----------------------------------------------------------------------------
def get_immediate_dependencies(
    sorted_records: List[Dict[str, Any]], file_name: str
) -> List[str]:
    deps: List[str] = []
    for rec in sorted_records:
        if file_name in rec.get("EXTRAS", {}).get("DEPENDENCIES", []):
            deps.append(rec["RENDERED_FILE_NAME"])
    return deps



def sort_file_records(
    file_records: List[Dict[str, Any]],
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
    verbose: int = 0,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Given a list of file_records (each dict must have keys:
      - "RENDERED_FILE_NAME"
      - "EXTRAS": { "DEPENDENCIES": [...] }
      - "PROCESS_TYPE": either "COPY" or "GENERATE"
      - plus additional keys as needed by render functions
    ) 
  
    Return them in topologically sorted order (or transitive subset if requested).
    Returns (sorted_records, next_idx).
    """
    total = len(file_records)
    if verbose >= 1:
        print(f"Sorting {total} file records (start_idx={start_idx}, start_file={start_file}, transitive={transitive})")

    try:
        if transitive and start_file:
            sorted_records = _transitive_dependency_sort(file_records, start_file)
            if verbose >= 1:
                print(f"  → Transitive sort from '{start_file}' yields {len(sorted_records)} files")
        else:
            sorted_records = _topological_sort(file_records)
            if verbose >= 1:
                print(f"  → Topological sort yields {len(sorted_records)} files")
    except Exception as e:
        raise RuntimeError(f"Failed to sort file records: {e}")

    # If start_file given but not transitive, skip up to that file
    if start_file and not transitive:
        idxs = [i for i, rec in enumerate(sorted_records) if rec.get("RENDERED_FILE_NAME") == start_file]
        if idxs:
            skip = idxs[0]
            sorted_records = sorted_records[skip:]
            if verbose >= 1:
                print(f"  → Skipping first {skip} files; processing {len(sorted_records)}")
        else:
            if verbose >= 1:
                print(f"  → start_file '{start_file}' not found; no skipping applied")

    # If numeric start_idx provided, skip that many
    if start_idx and start_idx > 0:
        if start_idx < len(sorted_records):
            if verbose >= 1:
                print(f"  → Skipping first {start_idx} files; processing {len(sorted_records) - start_idx}")
            sorted_records = sorted_records[start_idx:]
        else:
            sorted_records = []
            if verbose >= 1:
                print(f"  → start_idx {start_idx} >= total files; nothing to process")

    next_index = start_idx + len(sorted_records)
    return sorted_records, next_index
