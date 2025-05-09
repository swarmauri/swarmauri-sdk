# File: _processing.py
"""
processing.py

This module contains functions for processing file records within a project.
It supports:
  - COPY: render static templates.
  - GENERATE: render agent prompts and generate content via LLM.
"""

import os
from pprint import pformat
from typing import Any, Dict, List, Optional

from swarmauri_prompt_j2prompttemplate import j2pt

from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

from ._config import _config
from ._rendering import _render_copy_template, _render_generate_template
from ._graph import _build_forward_graph


def _save_file(
    content: str,
    filepath: str,
    logger: Optional[Any] = None,
    start_idx: int = 0,
    idx_len: int = 1,
) -> None:
    """
    Saves the given content to the specified file path.
    Creates the target directory if it does not exist.
    """
    try:
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        if logger:
            logger.info(f"({start_idx + 1}/{idx_len}) File saved: {filepath}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to save file '{filepath}': {e}")


def _create_context(
    file_record: Dict[str, Any],
    project_global_attributes: Dict[str, Any],
    logger: Optional[Any] = None,
):
    """
    Builds the rendering context for a single file record.
    """
    project_name = file_record.get("PROJECT_NAME")
    package_name = file_record.get("PACKAGE_NAME")
    module_name = file_record.get("MODULE_NAME")

    context: Dict[str, Any] = {}

    if project_name:
        context["PROJ"] = project_global_attributes
        context["PROJ"].setdefault("EXTRAS", {})

    if package_name:
        package = next(
            (pkg for pkg in project_global_attributes["PACKAGES"] if pkg["NAME"] == package_name),
            None,
        )
        if package:
            context["PKG"] = package
            context["PKG"].setdefault("EXTRAS", {})

    if module_name:
        module = None
        pkg = context.get("PKG")
        if pkg:
            module = next(
                (mod for mod in pkg.get("MODULES", []) if mod["NAME"] == module_name),
                None,
            )
        if module:
            context["MOD"] = module
            context["MOD"].setdefault("EXTRAS", {})

    context["FILE"] = file_record

    if logger:
        logger.debug(f"context:\n{pformat(context, indent=2)}")
    return context


def _process_file(
    file_record: Dict[str, Any],
    global_attrs: Dict[str, Any],
    template_dir: str,
    agent_env: Dict[str, Any],
    logger: Optional[Any] = None,
    start_idx: int = 0,
    idx_len: int = 1,
) -> bool:
    """
    Processes a single file record based on its PROCESS_TYPE.

    - For "COPY": renders and always saves (even if content is blank).
    - For "GENERATE": renders; if content generation returns None, skips save; if empty string, still saves.
    """
    context = _create_context(file_record, global_attrs, logger)
    final_filename = file_record.get("RENDERED_FILE_NAME")
    process_type = file_record.get("PROCESS_TYPE", "COPY").upper()

    if process_type == "COPY":
        content = _render_copy_template(file_record, context, logger)

    elif process_type == "GENERATE":
        if _config["revise"] and "agent_prompt_template_file" not in agent_env:
            agent_env["agent_prompt_template_file"] = "agent_revise.j2"

        if _config["revise"]:
            agent_prompt_template_name = agent_env["agent_prompt_template_file"]
            context["INJ"] = _config["revision_notes"]
        else:
            agent_prompt_template_name = file_record.get("AGENT_PROMPT_TEMPLATE", "agent_default.j2")

        agent_prompt_template_path = os.path.join(template_dir, agent_prompt_template_name)
        content = _render_generate_template(
            file_record, context, agent_prompt_template_path, agent_env, logger
        )

    else:
        if logger:
            logger.warning(
                f"Unknown PROCESS_TYPE '{process_type}' for file '{final_filename}'. Skipping."
            )
        return False

    # Handle None (failure) vs. empty string (blank file)
    if content is None:
        if logger:
            logger.warning(f"No content generated for file '{final_filename}'; skipping save.")
        return False

    if content == "":
        if logger:
            logger.warning(f"Blank content for file '{final_filename}'; saving empty file.")

    _save_file(content, final_filename, logger, start_idx, idx_len)
    return True


def _process_project_files(
    global_attrs: Dict[str, Any],
    file_records: List[Dict[str, Any]],
    template_dir: str,
    agent_env: Dict[str, Any],
    logger: Optional[Any] = None,
    start_idx: int = 0,
) -> None:
    """
    Processes all file records for a project, optionally in parallel, while respecting dependencies.

    If _config["workers"] > 0, files are rendered in parallel but only once their dependencies complete.
    Otherwise, files are rendered sequentially in sorted order.
    """
    idx_len = len(file_records) + start_idx
    workers = _config.get("workers", 0)

    if workers and workers > 0:
        forward_graph, in_degree, _ = _build_forward_graph(file_records)
        entry_map = {rec["RENDERED_FILE_NAME"]: rec for rec in file_records}
        idx_map = {
            rec["RENDERED_FILE_NAME"]: i + start_idx
            for i, rec in enumerate(file_records)
        }

        def _worker(fname: str) -> str:
            rec = entry_map[fname]
            idx = idx_map[fname]
            new_dir = rec.get("TEMPLATE_SET") or global_attrs.get("TEMPLATE_SET")
            if new_dir and str(j2pt.templates_dir[0]) != str(new_dir):
                if logger:
                    logger.debug(
                        "Template dir updated: "
                        f" '{j2pt.templates_dir[0]}' -> '{new_dir}'"
                    )
                j2pt.templates_dir[0] = str(new_dir)
            _process_file(rec, global_attrs, template_dir, agent_env, logger, idx, idx_len)
            return fname

        executor = ThreadPoolExecutor(max_workers=workers)
        futures = {}
        try:
            for fname, deps in in_degree.items():
                if deps == 0:
                    futures[executor.submit(_worker, fname)] = fname

            while futures:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for fut in done:
                    comp = futures.pop(fut)
                    for child in forward_graph.get(comp, []):
                        in_degree[child] -= 1
                        if in_degree[child] == 0:
                            futures[executor.submit(_worker, child)] = child
        except KeyboardInterrupt:
            executor.shutdown(wait=False)
            raise
        finally:
            executor.shutdown(wait=True)
        return

    for rec in file_records:
        new_dir = rec.get("TEMPLATE_SET") or global_attrs.get("TEMPLATE_SET")
        if new_dir and str(j2pt.templates_dir[0]) != str(new_dir):
            if logger:
                logger.debug(
                    "Template dir updated: "
                    f" '{j2pt.templates_dir[0]}' -> '{new_dir}'"
                )
            j2pt.templates_dir[0] = str(new_dir)

        if not _process_file(rec, global_attrs, template_dir, agent_env, logger, start_idx, idx_len):
            break
        start_idx += 1
