# peagen/core/process_core.py

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

from peagen._utils.config_loader import load_peagen_toml
from peagen.core.sort_core import sort_file_records

from peagen.core.render_core import _render_copy_template, _render_generate_template
from peagen.models import Task  # if task‐related logic is needed

def merge_cli_into_cfg(
    projects_payload: str,
    start_idx: Optional[int] = None,
    start_file: Optional[str] = None,
    transitive: bool = False,
    verbose: int = 0,
    output_base: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load .peagen.toml as the base config and override with any CLI flags that
    affect processing. Returns the merged config dict.
    """
    cfg = load_peagen_toml(".peagen.toml")
    cfg["projects_payload"] = projects_payload
    cfg["transitive"] = transitive
    cfg["verbose"] = verbose
    if output_base:
        cfg["output_base"] = output_base
    if start_idx is not None:
        cfg["start_idx"] = start_idx
    if start_file:
        cfg["start_file"] = start_file
    return cfg


def load_projects_payload(projects_payload_path: str) -> List[Dict[str, Any]]:
    """
    Read a YAML file containing a top-level 'PROJECTS' key.
    Returns a list of project dicts.
    """
    path = Path(projects_payload_path)
    if not path.exists():
        raise FileNotFoundError(f"Projects payload not found: {projects_payload_path}")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    projects = doc.get("PROJECTS")
    if not isinstance(projects, list):
        raise ValueError(f"YAML {projects_payload_path} must contain a top-level 'PROJECTS' list")
    return projects


def process_single_project(
    project: Dict[str, Any],
    cfg: Dict[str, Any],
    start_idx: int = 0,
    start_file: Optional[str] = None,
    transitive: bool = False,
    verbose: int = 0,
    output_base: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    1) Load file records from project dict (expects project["FILES"] to exist).
    2) Sort the file_records via sort_file_records.
    3) If output_base is provided, render each file under that directory.
    Returns (sorted_records, next_idx).
    """
    all_file_records = project.get("FILES", [])
    if not isinstance(all_file_records, list):
        raise ValueError(f"Project '{project.get('NAME')}' must contain a 'FILES' list")

    sorted_records, next_idx = sort_file_records(
        all_file_records,
        start_idx=start_idx,
        start_file=start_file,
        transitive=transitive,
        verbose=verbose,
    )

    if output_base and sorted_records:
        template_dir = cfg.get("template_base_dir", os.getcwd())
        agent_env = cfg.get("agent_env", {})
        j2pt = J2PromptTemplate()
        logger = cfg.get("logger")
        workspace_root = Path(output_base) / project.get("NAME", "UnnamedProject")
        workspace_root.mkdir(parents=True, exist_ok=True)

        # Process each sorted record
        for rec in sorted_records:
            process_type = rec.get("PROCESS_TYPE")
            rendered_name = rec.get("RENDERED_FILE_NAME")
            extras = rec.get("EXTRAS", {})
            context = {**project, **extras}

            if process_type == "COPY":
                content = _render_copy_template(rec, context, j2pt, logger)
                out_path = workspace_root / rendered_name
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content, encoding="utf-8")

            elif process_type == "GENERATE":
                prompt_tpl = rec.get("PROMPT_TEMPLATE")
                if not prompt_tpl:
                    if logger:
                        logger.error(f"No PROMPT_TEMPLATE for GENERATE file '{rendered_name}'; skipping.")
                    continue
                content = _render_generate_template(rec, context, prompt_tpl, j2pt, agent_env, logger)
                out_path = workspace_root / rendered_name
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content, encoding="utf-8")

            else:
                if logger:
                    logger.warning(f"Unknown PROCESS_TYPE '{process_type}' for file '{rendered_name}'; skipping.")

    return sorted_records, next_idx


def process_all_projects(
    projects_payload_path: str,
    cfg: Dict[str, Any],
    transitive: bool = False,
    verbose: int = 0,
    output_base: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    1) Load all projects from the payload YAML.
    2) For each project, call process_single_project.
    Returns a mapping: { project_name: [sorted_records], ... }.
    If output_base is provided, renders all files under output_base/<project_name>/.
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
            verbose=verbose,
            output_base=output_base,
        )
        results[name] = recs

    return results
