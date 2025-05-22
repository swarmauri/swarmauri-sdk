# File: _processing.py
"""Process COPY and GENERATE file records.

The module renders static templates or agent prompts and saves the
result to disk. It also supports optional remote uploads and manifest
streaming.
"""

import os
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from pprint import pformat
from typing import Any, Dict, List, Optional

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate, j2pt

from ._config import _config
from ._graph import _build_forward_graph
from ._rendering import _render_copy_template, _render_generate_template
from .manifest_writer import ManifestWriter


def _save_file(
    content: str,
    filepath: str,
    logger=None,
    start_idx: int = 0,
    idx_len: int = 1,
    *,
    storage_adapter=None,
    org: str | None = None,
    workspace_root: Path = Path("."),
    manifest_writer: Optional[ManifestWriter] = None,
) -> None:
    """
    1.  Write to <workspace_root>/<filepath>.
    2.  Optionally upload to the configured storage_adapter.
    3.  Stream a manifest line via ManifestWriter (if provided).
    """
    full_path = workspace_root / filepath
    try:
        os.makedirs(full_path.parent, exist_ok=True)
        with open(str(full_path), "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        if logger:
            logger.error(f"Failed to save file '{full_path}': {exc}")
        return

    if logger:
        fname = os.path.relpath(full_path, workspace_root)
        logger.info(f"({start_idx + 1}/{idx_len}) File saved: {fname}")

    if storage_adapter:  # remote upload
        key = os.path.normpath(filepath.lstrip("/"))
        with full_path.open("rb") as fsrc:
            storage_adapter.upload(key, fsrc)
        if logger:
            logger.info(f"({start_idx + 1}/{idx_len}) Uploaded → {key}")

    if manifest_writer:  # manifest line
        manifest_writer.add(
            {
                "file": filepath,
                "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )


def _create_context(
    file_record: Dict[str, Any],
    project_global_attributes: Dict[str, Any],
    logger: Optional[Any] = None,
) -> Dict[str, Any]:
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
            (
                pkg
                for pkg in project_global_attributes["PACKAGES"]
                if pkg["NAME"] == package_name
            ),
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
    j2_instance: Any | None = None,
    *,
    workspace_root: Path = Path("."),
    logger: Optional[Any] = None,
    start_idx: int = 0,
    idx_len: int = 1,
    storage_adapter: Optional[Any] = None,
    org: Optional[str] = None,
    manifest_writer: Optional[ManifestWriter] = None,  # NEW
) -> bool:
    """
    Render one file_record (COPY | GENERATE).
    """
    if j2_instance is None:
        j2_instance = J2PromptTemplate()
        if j2pt.templates_dir:
            j2_instance.templates_dir = [template_dir] + list(j2pt.templates_dir)
        else:
            j2_instance.templates_dir = [template_dir]

    context = _create_context(file_record, global_attrs, logger)
    final_filename = os.path.normpath(file_record.get("RENDERED_FILE_NAME"))
    process_type = file_record.get("PROCESS_TYPE", "COPY").upper()

    try:
        if process_type == "COPY":
            content = _render_copy_template(file_record, context, j2_instance)
        elif process_type == "GENERATE":
            if _config["revise"] and "agent_prompt_template_file" not in agent_env:
                agent_env["agent_prompt_template_file"] = "agent_revise.j2"
            if _config["revise"]:
                context["INJ"] = _config["revision_notes"]
                prompt_name = agent_env["agent_prompt_template_file"]
            else:
                prompt_name = file_record.get(
                    "AGENT_PROMPT_TEMPLATE", "agent_default.j2"
                )

            prompt_path = os.path.join(template_dir, prompt_name)
            content = _render_generate_template(
                file_record, context, prompt_path, j2_instance, agent_env
            )
        else:
            if logger:
                logger.warning(
                    f"Unknown PROCESS_TYPE '{process_type}' for file '{final_filename}'. Skipping."
                )
            return False
    except Exception as e:
        if logger:
            logger.error(f"Error rendering '{final_filename}': {e}")
        return False

    if content is None:
        if logger:
            logger.warning(f"No content generated for '{final_filename}'; skipping.")
        return False

    if content == "":
        if logger:
            logger.warning(
                f"Blank content for file '{final_filename}'; saving empty file."
            )

    save_kwargs = {}
    if storage_adapter is not None:
        save_kwargs["storage_adapter"] = storage_adapter
    if org is not None:
        save_kwargs["org"] = org
    if workspace_root != Path("."):
        save_kwargs["workspace_root"] = workspace_root
    if manifest_writer is not None:
        save_kwargs["manifest_writer"] = manifest_writer

    _save_file(
        content,
        final_filename,
        logger,
        start_idx,
        idx_len,
        **save_kwargs,
    )
    return True


def _process_project_files(
    global_attrs: Dict[str, Any],
    file_records: List[Dict[str, Any]],
    template_dir: str,
    agent_env: Dict[str, Any],
    logger: Optional[Any] = None,
    *,
    workspace_root: Path = Path("."),
    start_idx: int = 0,
    storage_adapter: Optional[Any] = None,
    org: Optional[str] = None,
    manifest_writer: Optional[ManifestWriter] = None,
) -> None:
    """
    Processes all file_records, creating fresh J2PromptTemplate instances
    and either parallel- or sequentially executing _process_file.
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

        def _worker(fname: str) -> None:
            rec = entry_map[fname]
            idx = idx_map[fname]
            new_dir = rec.get("TEMPLATE_SET") or global_attrs.get("TEMPLATE_SET")

            j2 = j2pt.copy(deep=False)
            j2.templates_dir = (
                [str(new_dir)] + [workspace_root] + list(j2.templates_dir[1:])
            )
            if str(new_dir) != j2pt.templates_dir[0]:
                j2pt.templates_dir = [str(new_dir)] + j2pt.templates_dir[1:]
                if logger:
                    logger.debug(f"Updated templates_dir to {new_dir}")
            try:
                _process_file(
                    rec,
                    global_attrs,
                    template_dir,
                    agent_env,
                    j2,
                    logger=logger,
                    start_idx=idx,
                    idx_len=idx_len,
                    storage_adapter=storage_adapter,
                    org=org,
                    workspace_root=workspace_root,
                    manifest_writer=manifest_writer,  # NEW
                )
            except Exception as e:
                logger.warning(f"{e}")

        executor = ThreadPoolExecutor(max_workers=workers)
        futures = {}
        try:
            # Launch initial tasks
            for fname, deps in in_degree.items():
                if deps == 0:
                    futures[executor.submit(_worker, fname)] = fname

            # As tasks complete, schedule their dependents
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

    # Sequential execution
    for rec in file_records:
        new_dir = rec.get("TEMPLATE_SET") or global_attrs.get("TEMPLATE_SET")
        if str(new_dir) != j2pt.templates_dir[0]:
            j2pt.templates_dir = [str(new_dir)] + j2pt.templates_dir[1:]
            if logger:
                logger.debug(f"Updated templates_dir to {new_dir}")

        j2_instance = J2PromptTemplate()
        j2_instance.templates_dir = (
            [str(new_dir)] + [workspace_root] + list(j2pt.templates_dir[1:])
        )

        if not _process_file(
            rec,
            global_attrs,
            template_dir,
            agent_env,
            j2_instance,
            logger,
            start_idx=start_idx,
            idx_len=idx_len,
            storage_adapter=storage_adapter,
            org=org,
            workspace_root=workspace_root,
            manifest_writer=manifest_writer,
        ):
            break
        start_idx += 1
