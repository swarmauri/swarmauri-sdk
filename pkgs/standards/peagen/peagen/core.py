"""Core workflow logic for Peagen.

This module contains the ``Peagen`` class which orchestrates file
generation, package handling and Jinja environment setup.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple

import peagen.plugin_registry
import peagen.templates
import yaml
from colorama import Fore, Style
from colorama import init as colorama_init
from pydantic import ConfigDict, Field, model_validator
from swarmauri_base import SubclassUnion
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.loggers.LoggerBase import LoggerBase
from swarmauri_prompt_j2prompttemplate import j2pt

from swarmauri_standard.loggers.Logger import Logger

from .manifest_writer import ManifestWriter
from .slug_utils import slugify
from ._config import __logger_name__, _config, __version__
from ._graph import _topological_sort, _transitive_dependency_sort
from ._processing import _process_project_files

colorama_init(autoreset=True)


class Peagen(ComponentBase):
    """Encapsulates payload → file-generation workflow."""

    # ── Inputs / ctor params ────────────────────────────────────────────
    projects_payload_path: str
    template_base_dir: Optional[str] = None
    org: Optional[str] = None

    storage_adapter: Optional[Any] = Field(default=None, exclude=True)
    agent_env: Dict[str, Any] = Field(default_factory=dict)
    j2pt: Any = Field(default_factory=lambda: j2pt)

    # Runtime / env setup
    base_dir: str = Field(exclude=True, default_factory=os.getcwd)

    # Legacy flag – converted to TEMPLATE_SETS during CLI parsing.
    additional_package_dirs: List[Path] = Field(
        default_factory=list,
        description="DEPRECATED – converted to SOURCE_PACKAGES at CLI level.",
    )

    # New: scratch workspace chosen by process.py
    workspace_root: Optional[Path] = Field(
        default=None,
        exclude=True,
        description="Workspace where generated & copied files live.",
    )

    # New: **authoritative list** of external packages copied into workspace.
    source_packages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Each item: {type:'git'|'local'|'bundle'|'uri', uri/archive, ref?, dest, "
            "expose_to_jinja?, checksum?}. 'dest' is relative to workspace_root."
        ),
    )

    # New: template-sets installed for this run
    template_sets: List[Dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Manifest entries for installed template-sets. "
            "Each item: {name, type:'pip'|'git'|'local'|'bundle', "
            "target, ref?, bundle_file?}."
        ),
    )

    # Internal state
    projects_list: List[Dict[str, Any]] = Field(default_factory=list, exclude=True)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict, exclude=True)
    in_degree: Dict[str, int] = Field(default_factory=dict, exclude=True)
    slug_map: Dict[str, str] = Field(default_factory=dict, exclude=True)

    namespace_dirs: List[str] = Field(default_factory=list)
    logger: SubclassUnion["LoggerBase"] = Logger(
        name=Fore.GREEN + __logger_name__ + Style.RESET_ALL
    )
    dry_run: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)
    version: str = __version__

    # ──────────────────────────────────────────────────────────────────
    # Environment setup (called automatically by Pydantic)
    # ──────────────────────────────────────────────────────────────────
    @model_validator(mode="after")
    def _setup_env(self) -> "Peagen":
        """
        Build the Jinja search path (`namespace_dirs`) **purely from directories
        that exist inside the workspace** plus built-ins & plugin templates.
        """
        # ── Auto-convert any leftover `additional_package_dirs`
        #    into synthetic 'local' TEMPLATE_SET entries, so they get
        #    written to the manifest without CLI help.
        # -----------------------------------------------------------
        ns_dirs: List[str] = list(peagen.templates.__path__)

        # 1) Template-set plugins discovered via registry
        from peagen.plugin_registry import registry

        for plugin in registry.get("template_sets", {}).values():
            pkg: ModuleType = (
                plugin
                if isinstance(plugin, ModuleType)
                else import_module(plugin.__module__.split(".", 1)[0])
            )
            if hasattr(pkg, "__path__"):
                ns_dirs.extend(str(p) for p in pkg.__path__)

        # 2) Workspace itself – always first so includes can reference freshly generated files
        if self.workspace_root is not None:
            ns_dirs.insert(0, os.fspath(self.workspace_root))

        # 3) Source-package *dest* folders exposed to Jinja
        for spec in self.source_packages:
            if spec.get("expose_to_jinja"):
                ns_dirs.append(
                    os.fspath(Path(self.workspace_root or ".") / spec["dest"])
                )

        # 4) Legacy additional_package_dirs (already copied by CLI helper into workspace)
        for p in self.additional_package_dirs:
            ns_dirs.append(os.fspath(p))

        # 5) User-specified template_base_dir and repo root
        if self.template_base_dir:
            ns_dirs.append(self.template_base_dir)
        ns_dirs.append(self.base_dir)

        # Finalise
        self.namespace_dirs = ns_dirs
        # j2pt expects *template search dirs* in templates_dir attr
        self.j2pt.templates_dir = ns_dirs

        return self

    # ──────────────────────────────────────────────────────────────────
    # Public helpers (unchanged except for search-path logic)
    # ──────────────────────────────────────────────────────────────────
    def update_templates_dir(self, package_specific_template_dir: str | Path) -> None:
        """
        Update Jinja search path for a package-specific render call.
        Still honours source_packages so templates can {% include %} from them.
        """
        dirs = [
            os.fspath(package_specific_template_dir),
            self.base_dir,
            *[
                os.fspath(Path(self.workspace_root or ".") / spec["dest"])
                for spec in self.source_packages
                if spec.get("expose_to_jinja")
            ],
        ]
        dirs.extend(os.fspath(p) for p in self.additional_package_dirs)
        self.j2pt.templates_dir = [os.path.normpath(d) for d in dirs]

    def locate_template_set(self, template_set: str) -> Path:
        """Search `namespace_dirs` for the given template-set folder."""
        for base in self.namespace_dirs:
            candidate = Path(base) / template_set
            if candidate.is_dir():
                return candidate.resolve()
        raise ValueError(
            f"Template set '{template_set}' not found in: {self.namespace_dirs}"
        )

    # ---------------------
    # Public Methods
    # ---------------------

    def load_projects(self) -> List[Dict[str, Any]]:
        """
        Loads projects from the global projects YAML file.
        Populates self.projects_list.

        Returns:
          list[dict]: A list of project dictionaries.
        """
        try:
            with open(self.projects_payload_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            # Assume the file contains a top-level "PROJECTS" key or is a list itself.
            if isinstance(data, dict):
                self.projects_list = data.get("PROJECTS", [])
            else:
                self.projects_list = data
            self.logger.info(
                "Loaded "
                + Fore.GREEN
                + f"{len(self.projects_list)}"
                + Style.RESET_ALL
                + f" projects from '{self.projects_payload_path}'."
            )
            # build slug map for quick lookup
            self.slug_map = {
                slugify(p.get("NAME", "")): p.get("NAME", "")
                for p in self.projects_list
                if p.get("NAME")
            }
        except Exception as e:
            self.logger.error(f"Failed to load projects: {e}")
            self.projects_list = []
        return self.projects_list

    def process_all_projects(self) -> list:
        """
        Processes all projects in self.projects_list.
        For each project, it renders the project YAML, processes file records,
        and (optionally) handles dependency ordering.
        """

        sorted_records = []
        if not self.projects_list:
            self.load_projects()
        self.logger.debug(f"Projects loaded: '{self.projects_list}'")
        for project in self.projects_list:
            file_records, start_idx = self.process_single_project(project)
            sorted_records.append(file_records)
        return sorted_records

    # -------------------------------------------------------------------
    # Remaining methods (process_single_project, etc.) are unchanged.
    # -------------------------------------------------------------------

    def process_single_project(
        self,
        project: Dict[str, Any],
        start_idx: int = 0,
        start_file: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Render & generate all files for *project*.

        Streaming manifests:
        --------------------
        *   A ManifestWriter is created before file processing begins.
        *   Each file save triggers writer.add(…).
        *   On successful completion we call writer.finalise().
        """
        all_file_records = []
        packages = project.get("PACKAGES", [])
        project_name = project.get("NAME", "UnnamedProject")

        # ------------------------------------------------------
        # PHASE 1: RENDER EACH PACKAGE’S ptree.yaml.j2
        # ------------------------------------------------------
        for pkg in packages:
            project_only_context = {"PROJ": project.copy()}
            project_only_context["PROJ"]["PKGS"] = [pkg]

            pkg_template_set = (
                pkg.get("TEMPLATE_SET_OVERRIDE")
                or pkg.get("TEMPLATE_SET", None)
                or project.get("TEMPLATE_SET", "default")
            )

            try:
                template_dir = self.locate_template_set(pkg_template_set)
                self.update_templates_dir(template_dir)
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
                self.j2pt.set_template(ptree_template_path)
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

        # ------------------------------------------------------
        # PHASE 2: DECIDE WHICH TOPOLOGICAL SORT METHOD
        # ------------------------------------------------------
        transitive = _config.get("transitive", False)

        try:
            if transitive:
                if start_file:
                    sorted_records = _transitive_dependency_sort(
                        all_file_records, start_file
                    )
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

            # ------------------------------------------------------
            # PHASE 3: HANDLE start_file EVEN IF NOT TRANSITIVE
            # ------------------------------------------------------
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
                        f"Requested start_file '{start_file}' not found; "
                        f"no skipping applied."
                    )

            # ------------------------------------------------------
            # PHASE 4: SKIP start_idx FILES
            # ------------------------------------------------------
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

        # ------------------------------------------------------
        # PHASE 5: PROCESS THE SORTED FILES (propagate original start_idx)
        # ------------------------------------------------------
        if not self.dry_run and sorted_records:
            # ------------------------------------------------------
            # Pass workspace_root into every file save/upload call
            # ------------------------------------------------------

            # choose workspace_root or fallback to base_dir
            root = self.workspace_root or Path(self.base_dir)

            workspace_uri = ""
            if self.storage_adapter:
                # best-effort generic inference
                for attr in ("workspace_uri", "base_uri", "root_uri"):
                    if hasattr(self.storage_adapter, attr):
                        workspace_uri = str(getattr(self.storage_adapter, attr))
                        break

            manifest_meta: Dict[str, Any] = {
                "schema_version": "3.1.0",
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
                agent_env=self.agent_env,
                logger=self.logger,
                storage_adapter=self.storage_adapter,
                org=self.org,
                workspace_root=root,
                start_idx=start_idx,
                manifest_writer=manifest_writer,
            )

            # --------  finalise manifest
            if manifest_writer.path.exists():
                final_path = manifest_writer.finalise()
                self.logger.info(
                    f"Manifest finalised → \n\t{Fore.YELLOW}{final_path}{Style.RESET_ALL} "
                    f"({len(sorted_records)} files, {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S UTC})"
                )
            else:
                self.logger.warning("Manifest file missing; skipping finalise.")

            # ────────────────────────────────────────────────────────────
            #  Log status
            # ────────────────────────────────────────────────────────────
            self.logger.info(
                f"Completed file generation workflow for org='{self.org}', "
                f"project='{project_name}'."
            )

        return (sorted_records, start_idx)
