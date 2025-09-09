"""
peagen.core.process_core
========================
Render, generate, and commit project files directly into the **existing
task work-tree** (created upstream by fetch/eval/mutate handlers).

Key points
----------
* **No storage adapters** – artefacts are normal Git-tracked files.
* **project_dir == worktree** – caller must supply it via cfg["worktree"].
* No legacy workspace_root / source_packages logic remains.
"""

from __future__ import annotations

import os
import yaml
from contextlib import suppress
from pathlib import Path
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple, Union

from swarmauri_standard.loggers.Logger import Logger
from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

from peagen._utils._context import _create_context
from peagen.core.sort_core import sort_file_records
from peagen.core.render_core import _render_copy_template, _render_generate_template
from peagen.plugins.vcs import GitVCS
from peagen._utils.slug_utils import slugify
from peagen._utils._search_template_sets import (
    build_global_template_search_paths,
    build_ptree_template_search_paths,
    build_file_template_search_paths,
)
from peagen.core.validate_core import _collect_errors
from peagen.jsonschemas import PROJECTS_PAYLOAD_V1_SCHEMA
from peagen.errors import (
    ProjectsPayloadValidationError,
    ProjectsPayloadFormatError,
    MissingProjectsListError,
)

logger = Logger(name=__name__)


# ───────────────────────── payload loader ────────────────────────────
def load_projects_payload(
    projects_payload: Union[str, PathLike[str], List[Dict[str, Any]], Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a list of project dicts parsed from *projects_payload*."""
    if isinstance(projects_payload, (list, dict)):
        doc: Any = projects_payload
    else:
        try:
            pp = Path(os.fspath(projects_payload))
            yaml_text = (
                pp.read_text(encoding="utf-8")
                if pp.is_file()
                else str(projects_payload)
            )
        except Exception:
            yaml_text = str(projects_payload)
        doc = yaml.safe_load(yaml_text)

    if isinstance(doc, list):
        return doc
    if not isinstance(doc, dict):
        raise ProjectsPayloadFormatError(type(doc).__name__, str(projects_payload))

    projects = doc.get("PROJECTS")
    if not isinstance(projects, list):
        raise MissingProjectsListError(str(projects_payload))

    errs = _collect_errors(doc, PROJECTS_PAYLOAD_V1_SCHEMA)
    if errs:
        raise ProjectsPayloadValidationError(errs, str(projects_payload))
    return projects


# ───────────────────── template-set helpers ─────────────────────────
def locate_template_set(
    template_set: str, search_paths: List[Path], log: Optional[Any] = None
) -> Path:
    """Locate *template_set* within *search_paths*."""
    log = log or logger
    for base in search_paths:
        cand = base / template_set
        if cand.is_dir():
            log.info(f"Template set '{template_set}' found at {cand}")
            return cand.resolve()
    raise ValueError(f"Template set '{template_set}' not found in {search_paths}")


# ───────────────────── ptree rendering ─────────────────────────────
def _render_package_ptree(
    project: Dict[str, Any],
    pkg: Dict[str, Any],
    global_search_paths: List[Path],
    project_dir: Path,
    log: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Render ptree.yaml.j2 for a package → list of file records."""
    log = log or logger
    pkg_name = pkg.get("NAME", "<pkg>")

    tmpl_name = (
        pkg.get("TEMPLATE_SET_OVERRIDE")
        or pkg.get("TEMPLATE_SET")
        or project.get("TEMPLATE_SET")
        or "default"
    )
    template_dir = locate_template_set(tmpl_name, global_search_paths, log)

    ptree_paths = build_ptree_template_search_paths(template_dir, Path.cwd())

    # Prepare render context
    proj_copy = dict(project, PKGS=[dict(pkg)])
    proj_copy.setdefault("EXTRAS", {})
    proj_copy["PKGS"][0].setdefault("EXTRAS", {})

    j2 = J2PromptTemplate()
    j2.templates_dir = ptree_paths

    ptree_tpl = template_dir / "ptree.yaml.j2"
    if not ptree_tpl.exists():
        log.warning(f"No ptree.yaml.j2 for package '{pkg_name}'. Skipping.")
        return []

    j2.set_template(ptree_tpl)
    rendered = j2.fill({"PROJ": proj_copy})

    # Save rendered ptree for debugging
    debug_dir = project_dir / ".peagen"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"{slugify(pkg_name)}_ptree.yaml").write_text(
        rendered, encoding="utf-8"
    )

    parsed = yaml.safe_load(rendered)
    records = (
        parsed["FILES"]
        if isinstance(parsed, dict) and "FILES" in parsed
        else parsed
        if isinstance(parsed, list)
        else []
    )

    for rec in records:
        rec["TEMPLATE_SET"] = str(template_dir)
        rec["PTREE_SEARCH_PATHS"] = [str(p) for p in ptree_paths]

    return records


# ───────────────────── file handlers ───────────────────────────────
def _handle_copy(
    rec: Dict[str, Any],
    context: Dict[str, Any],
    j2: J2PromptTemplate,
    project_dir: Path,
    commit_paths: List[Path],
) -> None:
    out_path = project_dir / rec["RENDERED_FILE_NAME"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render_copy_template(rec, context, j2) or "", encoding="utf-8")
    commit_paths.append(out_path)


def _handle_generate(
    rec: Dict[str, Any],
    context: Dict[str, Any],
    j2: J2PromptTemplate,
    agent_env: Dict[str, Any],
    cfg: Dict[str, Any],
    project_dir: Path,
    commit_paths: List[Path],
) -> None:
    prompt_tpl = rec.get("AGENT_PROMPT_TEMPLATE")
    if not prompt_tpl:
        logger.error(f"No AGENT_PROMPT_TEMPLATE for {rec['RENDERED_FILE_NAME']}")
        return
    content = _render_generate_template(rec, context, prompt_tpl, j2, agent_env, cfg)
    out_path = project_dir / rec["RENDERED_FILE_NAME"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content or "", encoding="utf-8")
    commit_paths.append(out_path)


# ───────────────────── project orchestrator ────────────────────────
def process_single_project(
    project: Dict[str, Any],
    cfg: Dict[str, Any],
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
) -> Tuple[List[Dict[str, Any]], int, str | None, List[str]]:
    """
    Render *project* inside ``cfg["worktree"]`` and optionally commit results.

    cfg must include:
        * worktree: Path to the task’s Git work-tree.
        * (optional) vcs:   GitVCS instance bound to that work-tree.
        * (optional) logger: custom logger.
        * (optional) agent_env / other generation config.
    """
    if "worktree" not in cfg:
        raise KeyError("cfg['worktree'] is required (path to task work-tree)")

    log = cfg.get("logger") or logger
    name = project.get("NAME", "<project>")
    project_dir = Path(cfg["worktree"]).resolve()
    log.info(f"========== Processing '{name}' in work-tree {project_dir} ==========")

    global_paths = build_global_template_search_paths(base_dir=Path.cwd())

    # 1. Collect file records
    records: List[Dict[str, Any]] = []
    for pkg in project.get("PACKAGES", []):
        records.extend(
            _render_package_ptree(project, pkg, global_paths, project_dir, log)
        )

    # 2. Topological sort
    sorted_records, next_idx = sort_file_records(
        records, start_idx, start_file, transitive
    )
    if not sorted_records:
        return sorted_records, next_idx, None, []

    # 3. Render files
    commit_paths: List[Path] = []
    vcs: GitVCS | None = cfg.get("vcs")

    for idx, rec in enumerate(sorted_records, start=start_idx):
        log.info(f"--- Rendering [{idx}] {rec['RENDERED_FILE_NAME']} ---")
        j2 = J2PromptTemplate()
        j2.templates_dir = build_file_template_search_paths(
            Path(rec["TEMPLATE_SET"]).resolve(),
            [Path(p) for p in rec["PTREE_SEARCH_PATHS"]],
        )

        ctx = _create_context(rec, project, log)
        if rec.get("PROCESS_TYPE", "COPY").upper() == "COPY":
            _handle_copy(rec, ctx, j2, project_dir, commit_paths)
        else:
            _handle_generate(
                rec,
                ctx,
                j2,
                cfg.get("agent_env", {}),
                cfg,
                project_dir,
                commit_paths,
            )

    # 4. Commit
    commit_sha: str | None = None
    oids: List[str] = []
    if vcs and commit_paths:
        repo_root = Path(vcs.repo.working_tree_dir)
        rels = [os.path.relpath(p, repo_root) for p in commit_paths]
        commit_sha = vcs.commit(rels, f"process {name}")
        for rel in rels:
            with suppress(Exception):
                oids.append(vcs.blob_oid(rel, ref=commit_sha))
        vcs.push(vcs.repo.active_branch.name)

    log.info(f"========== Completed '{name}' ==========\n")
    return sorted_records, next_idx, commit_sha, oids


# ───────────────────── payload orchestrator ────────────────────────
def process_all_projects(
    projects_payload: Union[str, List[Dict[str, Any]], Dict[str, Any]],
    cfg: Dict[str, Any],
    transitive: bool = False,
) -> Dict[str, List[Dict[str, Any]]]:
    """Render & commit every project described by *projects_payload*."""
    projects = load_projects_payload(projects_payload)
    aggregate: Dict[str, List[Dict[str, Any]]] = {}
    idx = 0

    for proj in projects:
        name = proj.get("NAME", f"project_{idx}")
        recs, idx, _, _ = process_single_project(
            proj, cfg, start_idx=idx, transitive=transitive
        )
        aggregate[name] = recs

    return aggregate
