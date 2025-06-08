# peagen/core/process_core.py

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

from peagen._utils._context import _create_context
from peagen.core.sort_core import sort_file_records
from peagen.core.render_core import _render_copy_template, _render_generate_template
from peagen.core.manifest_writer import ManifestWriter
from peagen._utils.slug_utils import slugify

from peagen._utils._search_template_sets import (
    build_global_template_search_paths,
    build_ptree_template_search_paths,
    build_file_template_search_paths,
)


def load_projects_payload(projects_payload: str) -> List[Dict[str, Any]]:
    """Return the list of projects from a payload string or path.

    ``projects_payload`` may be either the YAML text itself or a filesystem
    path pointing to a YAML file containing a top-level ``PROJECTS`` key.
    """

    try:
        maybe_path = Path(projects_payload)
        if maybe_path.is_file():
            yaml_text = maybe_path.read_text(encoding="utf-8")
        else:
            yaml_text = projects_payload
    except (OSError, TypeError):
        yaml_text = projects_payload

    doc = yaml.safe_load(yaml_text)
    projects = doc.get("PROJECTS") if isinstance(doc, dict) else doc
    if not isinstance(projects, list):
        raise ValueError("Payload must contain a top-level 'PROJECTS' list")
    return projects


def locate_template_set(
    template_set: str, search_paths: List[Path], logger: Optional[Any] = None
) -> Path:
    """
    Given a template_set name and a list of base directories, return the first
    Path(base_dir)/template_set that exists as a directory. Otherwise raise.
    """
    print(f"Locating template set '{template_set}' in search paths:")
    for idx, p in enumerate(search_paths):
        print(f"  [{idx}] {p}")

    for base in search_paths:
        candidate = Path(base) / template_set
        if candidate.is_dir():
            print(f"Found template set '{template_set}' at: {candidate}")
            return candidate.resolve()

    raise ValueError(
        f"Template set '{template_set}' not found in any of: {search_paths}"
    )


def _render_package_ptree(
    project: Dict[str, Any],
    pkg: Dict[str, Any],
    global_search_paths: List[Path],
    workspace_root: Path,
    logger: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    1) Determine which template set directory to use for this package.
    2) Build a dedicated ptree search path via build_ptree_template_search_paths().
    3) Render ptree.yaml.j2 within that directory, passing in {"PROJ": project_with_pkg}.
    4) Parse the rendered YAML into a list of file-record dicts.
    5) Attach "TEMPLATE_SET": template_dir and "PTREE_SEARCH_PATHS": ptree_paths to each record.
    6) Return the list of records (possibly empty).
    """
    pkg_name = pkg.get("NAME", "<no-package-name>")
    print(f"--- Rendering ptree for package '{pkg_name}' ---")

    tmpl_name = (
        pkg.get("TEMPLATE_SET_OVERRIDE")
        or pkg.get("TEMPLATE_SET")
        or project.get("TEMPLATE_SET")
        or "default"
    )
    print(f"Using template set name: '{tmpl_name}' for package '{pkg_name}'")

    # 1) Locate the package’s template directory using the global search paths
    template_dir = locate_template_set(tmpl_name, global_search_paths, logger)

    # 2) Build ptree search paths
    base_dir = Path(os.getcwd())
    ptree_paths = build_ptree_template_search_paths(
        package_template_dir=template_dir,
        base_dir=base_dir,
        workspace_root=workspace_root,
        source_packages=project.get("SOURCE_PACKAGES", []),
    )
    print(f"Built ptree search paths for '{pkg_name}':")
    for idx, p in enumerate(ptree_paths):
        print(f"  [{idx}] {p}")

    # 3) Render ptree.yaml.j2 with correct context
    project_copy = dict(project)  # shallow copy of the project dict
    project_copy["PKGS"] = [pkg]

    j2 = J2PromptTemplate()
    j2.templates_dir = ptree_paths

    ptree_path = Path(template_dir) / "ptree.yaml.j2"
    if not ptree_path.exists():
        if logger:
            logger.warning(
                f"No ptree.yaml.j2 found in {template_dir} for package '{pkg_name}'. Skipping."
            )
        return []

    j2.set_template(ptree_path)
    rendered = j2.fill({"PROJ": project_copy})
    print(
        f"Rendered ptree.yaml.j2 for package '{pkg_name}' (length: {len(rendered)} chars)"
    )

    # 4) Parse YAML
    try:
        parsed = yaml.safe_load(rendered)
    except Exception as e:
        raise ValueError(f"Failed to parse YAML for package '{pkg_name}': {e}")

    if isinstance(parsed, dict) and "FILES" in parsed:
        pkg_file_records = parsed["FILES"]
    elif isinstance(parsed, list):
        pkg_file_records = parsed
    else:
        if logger:
            logger.warning(
                f"Rendered ptree.yaml.j2 did not yield a list or 'FILES' for package '{pkg_name}'"
            )
        return []

    # 5) Attach metadata to each record
    for rec in pkg_file_records:
        rec["TEMPLATE_SET"] = str(template_dir)
        rec["PTREE_SEARCH_PATHS"] = [str(p) for p in ptree_paths]

    print(f" - Found {len(pkg_file_records)} file-record(s) for package '{pkg_name}'")

    return pkg_file_records


def _handle_copy(
    rec: Dict[str, Any],
    context: Dict[str, Any],
    j2: J2PromptTemplate,
    workspace_root: Path,
    storage_adapter: Any,
    project_name: str,
    logger: Optional[Any],
    manifest_writer: ManifestWriter,
) -> None:
    """
    Render a COPY record and save/upload it, then add to the manifest.
    """
    rendered_name = rec.get("RENDERED_FILE_NAME")
    print(f"Processing COPY file '{rendered_name}'")

    content = _render_copy_template(rec, context, j2, logger)
    out_path = workspace_root / rendered_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content or "", encoding="utf-8")

    print(f" - Saved COPY to {out_path}")

    if storage_adapter:
        key = f"{project_name}/{rendered_name}"
        with open(out_path, "rb") as fsrc:
            storage_adapter.upload(key, fsrc)
        print(f" - Uploaded COPY to storage key: {key}")

    manifest_writer.add(
        {
            "file": rendered_name,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    print(f" - Manifest entry added for '{rendered_name}'")


def _handle_generate(
    rec: Dict[str, Any],
    context: Dict[str, Any],
    j2: J2PromptTemplate,
    agent_env: Dict[str, Any],
    cfg: Dict[str, Any],
    workspace_root: Path,
    storage_adapter: Any,
    project_name: str,
    logger: Optional[Any],
    manifest_writer: ManifestWriter,
) -> None:
    """
    Render a GENERATE record by calling the external agent, save/upload it, then add to the manifest.
    """
    rendered_name = rec.get("RENDERED_FILE_NAME")
    print(f"Processing GENERATE file '{rendered_name}'")

    prompt_tpl = rec.get("AGENT_PROMPT_TEMPLATE")
    print(prompt_tpl)
    if not prompt_tpl:
        if logger:
            logger.error(
                f"No AGENT_PROMPT_TEMPLATE for GENERATE file '{rendered_name}'; skipping."
            )
        return

    content = _render_generate_template(
        rec,
        context,
        prompt_tpl,
        j2,
        agent_env,
        cfg,
    )
    print(content)
    out_path = workspace_root / rendered_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content or "", encoding="utf-8")

    print(f" - Saved GENERATE to {out_path}")

    if storage_adapter:
        key = f"{project_name}/{rendered_name}"
        with open(out_path, "rb") as fsrc:
            storage_adapter.upload(key, fsrc)
        print(f" - Uploaded GENERATE to storage key: {key}")

    manifest_writer.add(
        {
            "file": rendered_name,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    print(f" - Manifest entry added for '{rendered_name}'")


def process_single_project(
    project: Dict[str, Any],
    cfg: Dict[str, Any],
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    1) Build a global Jinja search path that includes built-ins, plugins, and workspace.
    2) For each package in project["PACKAGES"]:
       a) Locate and render its ptree.yaml.j2 → file records.
    3) Topologically sort all collected file records.
    4) If sorted_records is nonempty:
       a) Write each file (COPY or GENERATE) under the default output (<cwd>/<project_name>/…).
       b) Upload to storage if a storage_adapter is in cfg (optional).
       c) Stream each saved file into a ManifestWriter, finalize at end.
       d) Populate cfg["manifest_path"] with the manifest's final path.
    Returns (sorted_records, next_idx).
    """
    logger = cfg.get("logger")
    project_name = project.get("NAME", "<no-project-name>")

    print(f"========== Starting process for project '{project_name}' ==========")

    # ─── STEP 1: Build global search paths ─────────────────────────────────
    base_dir = Path(os.getcwd())
    source_pkgs = cfg.get("source_packages", [])

    # Always materialize workspace_root under the current working directory:
    workspace_root = Path(base_dir) / project_name
    workspace_root.mkdir(parents=True, exist_ok=True)

    global_search_paths = build_global_template_search_paths(
        workspace_root=workspace_root,
        source_packages=source_pkgs,
        base_dir=base_dir,
    )
    print("Global Jinja search paths:")
    for idx, p in enumerate(global_search_paths):
        print(f"  [{idx}] {p}")

    # ─── STEP 2: Render each package’s ptree.yaml.j2 → file records ─────
    all_file_records: List[Dict[str, Any]] = []
    for pkg in project.get("PACKAGES", []):
        pkg_records = _render_package_ptree(
            project=project,
            pkg=pkg,
            global_search_paths=global_search_paths,
            workspace_root=workspace_root,
            logger=logger,
        )
        all_file_records.extend(pkg_records)
    print(f"Total file-records collected: {len(all_file_records)}")

    # ─── STEP 3: Topological sort ─────────────────────────────────────────
    sorted_records, next_idx = sort_file_records(
        file_records=all_file_records,
        start_idx=start_idx,
        start_file=start_file,
        transitive=transitive,
    )
    print(f"Topologically sorted, {len(sorted_records)} files to process.")

    if not sorted_records:
        if logger:
            logger.warning(
                f"No files to process for project '{project_name}'. Exiting."
            )
        return sorted_records, next_idx

    # ─── STEP 4: Prepare manifest (workspace already exists) ───────────────
    storage_adapter = cfg.get("storage_adapter")
    workspace_uri = None
    if storage_adapter:
        for attr in ("workspace_uri", "base_uri", "root_uri"):
            if hasattr(storage_adapter, attr):
                workspace_uri = getattr(storage_adapter, attr)
                break

    manifest_meta = {
        "schema_version": 3,
        "workspace_uri": workspace_uri,
        "project": project_name,
        "source_packages": source_pkgs,
        "peagen_version": cfg.get("peagen_version", None),
    }
    manifest_dir = workspace_root / ".peagen"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest_writer = ManifestWriter(
        slug=slugify(project_name),
        adapter=storage_adapter,
        tmp_root=manifest_dir,
        meta=manifest_meta,
    )
    print(f"Processing files under: {workspace_root}")
    print("Beginning file-by-file rendering:")

    # ─── STEP 5: Render & save each sorted file ───────────────────────────
    for idx, rec in enumerate(sorted_records, start=start_idx):
        rendered_name = rec.get("RENDERED_FILE_NAME")
        if logger:
            logger.info(f"--- File [{idx}] '{rendered_name}' ---")

        j2 = J2PromptTemplate()

        record_dir = Path(rec.get("TEMPLATE_SET", "")).resolve()
        ptree_paths = [Path(p) for p in rec.get("PTREE_SEARCH_PATHS", [])]
        print("Pt ree search paths for this file:")
        for i, p in enumerate(ptree_paths):
            print(f"  [{i}] {p}")

        file_paths = build_file_template_search_paths(
            record_template_dir=record_dir,
            workspace_root=workspace_root,
            ptree_search_paths=ptree_paths,
        )
        j2.templates_dir = file_paths

        print("Final Jinja search paths for file:")
        for i, p in enumerate(file_paths):
            print(f"  [{i}] {p}")

        context = _create_context(rec, project, logger)

        process_type = rec.get("PROCESS_TYPE", "COPY").upper()
        print(process_type)
        if process_type == "COPY":
            print("\n\n\n\ncfg:", cfg)
            _handle_copy(
                rec,
                context,
                j2,
                workspace_root,
                storage_adapter,
                project_name,
                logger,
                manifest_writer,
            )
        elif process_type == "GENERATE":
            print("\n\n\n\ncfg:", cfg)
            _handle_generate(
                rec,
                context,
                j2,
                cfg.get("agent_env", {}),
                cfg,
                workspace_root,
                storage_adapter,
                project_name,
                logger,
                manifest_writer,
            )
        else:
            if logger:
                logger.warning(
                    f"Unknown PROCESS_TYPE '{process_type}' for file '{rendered_name}'; skipping."
                )

    # ─── STEP 6: Finalize manifest ────────────────────────────────────────
    # final_manifest_path = manifest_writer.finalise()
    # cfg["manifest_path"] = str(final_manifest_path)
    # print(f"Manifest written to: {final_manifest_path}")
    print(f"========== Completed project '{project_name}' ==========\n")

    return sorted_records, next_idx


def process_all_projects(
    projects_payload_path: str,
    cfg: Dict[str, Any],
    transitive: bool = False,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    1) Load all projects from the payload YAML.
    2) For each project, call process_single_project.
    Returns a mapping: { project_name: [sorted_records], ... }.
    Renders all files under <cwd>/<project_name>/ by default.
    """
    projects = load_projects_payload(projects_payload_path)
    results: Dict[str, List[Dict[str, Any]]] = {}
    next_idx = 0

    for proj in projects:
        name = proj.get("NAME", f"project_{next_idx}")
        recs, next_idx = process_single_project(
            proj,
            cfg,
            start_idx=next_idx,
            start_file=None,
            transitive=transitive,
        )
        results[name] = recs

    return results
