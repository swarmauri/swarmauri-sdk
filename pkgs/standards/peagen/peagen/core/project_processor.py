from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from colorama import Fore, Style
from pydantic import FilePath

from ..manifest_writer import ManifestWriter
from .._config import __version__, _config
from .._graph import _topological_sort, _transitive_dependency_sort
from .._utils._processing import _process_project_files
from .._utils.slug_utils import slugify
from .template_manager import TemplateManager


class ProjectProcessor:
    """Process projects into rendered files."""

    def __init__(
        self,
        template_manager: TemplateManager,
        j2pt: Any,
        agent_env: Dict[str, Any],
        logger,
        storage_adapter: Any = None,
        org: Optional[str] = None,
        workspace_root: Path | None = None,
        source_packages: List[Dict[str, Any]] | None = None,
        template_sets: List[Dict[str, Any]] | None = None,
        dry_run: bool = False,
    ) -> None:
        self.template_manager = template_manager
        self.j2pt = j2pt
        self.agent_env = agent_env
        self.logger = logger
        self.storage_adapter = storage_adapter
        self.org = org
        self.workspace_root = workspace_root
        self.source_packages = source_packages or []
        self.template_sets = template_sets or []
        self.dry_run = dry_run
        self.slug_map: Dict[str, str] = {}

    def process_all_projects(self, projects_list: List[Dict[str, Any]]) -> list:
        if self.logger:
            self.logger.debug("Beginning processing of all projects")
        sorted_records = []
        for project in projects_list:
            if self.logger:
                self.logger.debug(f"Starting project {project.get('NAME')}")
            file_records, _ = self.process_single_project(project)
            sorted_records.append(file_records)
        return sorted_records

    def process_single_project(
        self,
        project: Dict[str, Any],
        start_idx: int = 0,
        start_file: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        if self.logger:
            self.logger.debug(f"Processing project {project.get('NAME')}")
        all_file_records = []
        packages = project.get("PACKAGES", [])
        project_name = project.get("NAME", "UnnamedProject")

        for pkg in packages:
            project_only_context = {"PROJ": project.copy()}
            project_only_context["PROJ"]["PKGS"] = [pkg]

            pkg_template_set = (
                pkg.get("TEMPLATE_SET_OVERRIDE")
                or pkg.get("TEMPLATE_SET", None)
                or project.get("TEMPLATE_SET", "default")
            )

            try:
                template_dir = self.template_manager.locate_template_set(pkg_template_set)
                self.template_manager.update_templates_dir(template_dir)
            except ValueError as e:
                self.logger.error(
                    f"[{project_name}] Package '{pkg.get('NAME')}' error: {e}"
                )
                continue

            ptree_template_path = os.path.join(template_dir, "ptree.yaml.j2")
            if not os.path.isfile(ptree_template_path):
                self.logger.error(
                    f"[{project_name}] Missing ptree.yaml.j2 in template dir "
                    f"{template_dir} for package '{pkg.get('NAME')}'."
                )
                continue

            try:
                self.j2pt.set_template(FilePath(ptree_template_path))
                rendered_yaml_str = self.j2pt.fill(project_only_context)
            except Exception as e:
                self.logger.error(
                    f"[{project_name}] Ptree render failure for package "
                    f"'{pkg.get('NAME')}': {e}"
                )
                continue

            try:
                partial_data = yaml.safe_load(rendered_yaml_str)
            except yaml.YAMLError as e:
                self.logger.error(
                    f"[{project_name}] YAML parse failure for '{pkg.get('NAME')}': {e}"
                )
                continue

            if isinstance(partial_data, dict) and "FILES" in partial_data:
                pkg_file_records = partial_data["FILES"]
            elif isinstance(partial_data, list):
                pkg_file_records = partial_data
            else:
                self.logger.warning(
                    f"[{project_name}] Unexpected YAML structure from "
                    f"package '{pkg.get('NAME')}'; skipping."
                )
                continue

            for record in pkg_file_records:
                record["TEMPLATE_SET"] = template_dir

            all_file_records.extend(pkg_file_records)

        if not all_file_records:
            self.logger.warning(f"[{project_name}] No file records found at all.")
            return ([], 0)

        transitive = _config.get("transitive", False)

        try:
            if transitive:
                if start_file:
                    sorted_records = _transitive_dependency_sort(all_file_records, start_file)
                    self.logger.info(
                        f"Transitive sort for '{start_file}' on project '{project_name}', "
                        f"yielding {len(sorted_records)} files."
                    )
                else:
                    sorted_records = _topological_sort(all_file_records)
                    self.logger.info(
                        f"Full transitive sort ({len(sorted_records)} files) "
                        f"on project '{project_name}'."
                    )
            else:
                sorted_records = _topological_sort(all_file_records)
                self.logger.info(
                    f"Non-transitive sort ({len(sorted_records)} files) "
                    f"on project '{project_name}'."
                )

            if start_file and not transitive:
                found_index = next(
                    (
                        i
                        for i, fr in enumerate(sorted_records)
                        if fr.get("RENDERED_FILE_NAME") == start_file
                    ),
                    None,
                )
                if found_index is not None:
                    self.logger.info(
                        f"Skipping all files before '{start_file}' (index {found_index})."
                    )
                    sorted_records = sorted_records[found_index:]
                else:
                    self.logger.warning(
                        f"Requested start_file '{start_file}' not found; no skipping applied."
                    )

            if start_idx > 0:
                to_process_count = max(0, len(sorted_records) - start_idx)
                self.logger.info(
                    f"Skipping first {start_idx} file(s). "
                    f"Processing {to_process_count} remaining files for '{project_name}'."
                )
                sorted_records = sorted_records[start_idx:]
        except Exception as e:
            self.logger.error(f"[{project_name}] Failed to topologically sort: {e}")
            return ([], 0)

        if not self.dry_run and sorted_records:
            root = self.workspace_root or Path(self.template_manager.cwd)

            workspace_uri = ""
            if self.storage_adapter:
                for attr in ("workspace_uri", "base_uri", "root_uri"):
                    if hasattr(self.storage_adapter, attr):
                        workspace_uri = str(getattr(self.storage_adapter, attr))
                        break

            manifest_meta: Dict[str, Any] = {
                "schemaVersion": "3.1.0",
                "workspace_uri": workspace_uri,
                "project": project_name,
                "source_packages": self.source_packages,
                "template_sets": self.template_sets,
                "peagen_version": __version__,
            }

            project_slug = slugify(project_name)
            self.slug_map.setdefault(project_slug, project_name)
            manifest_writer: Optional[ManifestWriter] = None
            manifest_writer = ManifestWriter(
                slug=project_slug,
                adapter=self.storage_adapter,
                tmp_root=root / ".peagen",
                meta=manifest_meta,
            )

            _process_project_files(
                global_attrs=project,
                file_records=sorted_records,
                template_dir=template_dir,
                j2pt=self.j2pt,
                agent_env=self.agent_env,
                logger=self.logger,
                storage_adapter=self.storage_adapter,
                org=self.org,
                workspace_root=root,
                start_idx=start_idx,
                manifest_writer=manifest_writer,
            )
            if self.logger:
                self.logger.debug(
                    f"Processed {len(sorted_records)} files for project '{project_name}'"
                )

            if manifest_writer.path.exists():
                final_path = manifest_writer.finalise()
                self.logger.info(
                    f"Manifest finalised → \n\t{Fore.YELLOW}{final_path}{Style.RESET_ALL} "
                    f"({len(sorted_records)} files, {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S UTC})"
                )
            else:
                self.logger.warning("Manifest file missing; skipping finalise.")

            self.logger.info(
                f"Completed file generation workflow for org='{self.org}', "
                f"project='{project_name}'."
            )

        if self.logger:
            self.logger.debug(
                f"Returning {len(sorted_records)} sorted records for project '{project_name}'"
            )
        return (sorted_records, start_idx)
