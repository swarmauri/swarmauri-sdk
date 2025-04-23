"""
core.py

This module defines the main class for the file generation workflow.
The Peagen class encapsulates the overall workflow:
  - Loading global project data from a YAML file.
  - Rendering project YAML from a .yaml.j2 template.
  - Expanding file records (with package and module context).
  - Building and ordering a dependency graph.
  - Processing files (via "COPY" or "GENERATE" modes).
  - Querying dependencies and dependents.
  - Updating and saving both the global projects YAML and the template (.yaml.j2) file.
  - Starting processing from an arbitrary point (project, package, module, or file).

This class uses helper methods from modules such as:
  - rendering.py (for rendering templates and fields)
  - processing.py (for processing file records)
  - graph.py (for dependency graph construction and topological sorting)
  - updates.py (for updating and saving configuration data)
  - dependencies.py (for resolving and querying dependencies)
  - external.py (for calling external agents and chunking content)
"""

from colorama import init as colorama_init, Fore, Style
import os
import yaml
from typing import Any, Dict, List, Optional, Tuple
from pydantic import FilePath

from pathlib import Path

# Import helper modules from our package.
from ._processing import _process_project_files
from ._graph import _topological_sort, _transitive_dependency_sort
from ._Jinja2PromptTemplate import j2pt
from ._config import _config

import peagen.templates
from pydantic import Field, ConfigDict, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base import SubclassUnion
from swarmauri_standard.loggers.Logger import Logger
from swarmauri_base.loggers.LoggerBase import LoggerBase

colorama_init(autoreset=True)


class Peagen(ComponentBase):
    projects_payload_path: str
    template_base_dir: Optional[str] = None
    agent_env: Dict[str, Any] = Field(default_factory=dict)
    j2pt: Any = Field(default_factory=lambda: j2pt)  # adjust type as needed

    # Derived attributes with default factories:
    base_dir: str = Field(exclude=True, default_factory=os.getcwd)
    additional_package_dirs: List[Path] = Field(exclude=True, default=list)
    projects_list: List[Dict[str, Any]] = Field(exclude=True, default_factory=list)
    dependency_graph: Dict[str, List[str]] = Field(exclude=True, default_factory=dict)
    in_degree: Dict[str, int] = Field(exclude=True, default_factory=dict)

    # These will be computed in the validator:
    namespace_dirs: List[str] = Field(default_factory=list)
    logger: SubclassUnion[LoggerBase] = Logger(
        name=Fore.GREEN + "pfg" + Style.RESET_ALL
    )
    dry_run: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)
    version: str = "0.1.0"

    @model_validator(mode="after")
    def setup_env(self) -> "Peagen":
        # Gather all physical directories that provide peagen.templates:
        namespace_dirs = list(peagen.templates.__path__)  # installed template dirs
        initial_dirs = []
        initial_dirs.extend(self.additional_package_dirs)
        namespace_dirs.append(self.base_dir)  # include current working directory
        initial_dirs.append(self.base_dir)
        if self.template_base_dir:
            namespace_dirs.append(self.template_base_dir)
            initial_dirs.append(self.template_base_dir)
        self.namespace_dirs = namespace_dirs
        # Update the prompt template engine's templates directory list.
        self.j2pt.templates_dir = initial_dirs
        return self

    # ---------------------
    # J2PT Methods
    # ---------------------

    def update_templates_dir(self, package_specific_template_dir):
        dirs = [
            package_specific_template_dir,
            self.base_dir,
        ]
        dirs.extend(self.additional_package_dirs)
        dirs = [os.path.normpath(_d) for _d in dirs]
        self.j2pt.templates_dir = dirs

    def get_template_dir_any(self, template_set: str) -> Path:
        """
        Searches each directory in `self.namespace_dirs` for a subfolder
        named `template_set`. Returns the first match as a *Path*, or raises a ValueError.
        """
        for base_dir in self.namespace_dirs:
            # base_dir could be a string or Path – let's ensure it's a Path:
            base_dir_path = Path(base_dir)
            candidate = base_dir_path / template_set
            if candidate.is_dir():
                # Return a resolved Path object (absolute)
                return candidate.resolve()
        raise ValueError(
            f"Template set '{template_set}' not found in any of: {self.namespace_dirs}"
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

    def process_single_project(
        self,
        project: Dict[str, Any],
        start_idx: int = 0,
        start_file: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        1) For each package in the project, render its ptree.yaml.j2 to get file records.
        2) Combine those records into a single list.
        3) Depending on _config['transitive']:
           - If transitive=True and start_file is set, use _transitive_dependency_sort.
           - If transitive=True and start_file is not set, use _topological_sort.
           - If transitive=False, always use _topological_sort.
        4) Even if transitive=False, still honor start_file by skipping up to that file's index in the sorted list.
        5) Skip start_idx files.
        6) Process the remaining files.
        """

        all_file_records = []

        packages = project.get("PACKAGES", [])
        project_name = project.get("NAME", "UnnamedProject")

        # ------------------------------------------------------
        # PHASE 1: RENDER EACH PACKAGE’S ptree.yaml.j2
        # ------------------------------------------------------
        for pkg in packages:
            project_only_context = {}
            project_only_context["PROJ"] = project.copy()
            project_only_context["PROJ"]["PKGS"] = [pkg]

            pkg_template_set = (
                pkg.get("TEMPLATE_SET_OVERRIDE")
                or pkg.get("TEMPLATE_SET", None)
                or project.get("TEMPLATE_SET", "default")
            )

            try:
                template_dir = self.get_template_dir_any(pkg_template_set)
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

        # ------------------------------------------------------
        # PHASE 2: DECIDE WHICH TOPOLOGICAL SORT METHOD
        # ------------------------------------------------------
        transitive = _config.get("transitive", False)

        try:
            if transitive:
                # If transitive is True and a specific file is given,
                # return only the transitive closure for that file.
                if start_file:
                    sorted_records = _transitive_dependency_sort(
                        all_file_records, start_file
                    )
                    self.logger.info(
                        f"Transitive sort for '{start_file}' on project '{project_name}', "
                        f"yielding {len(sorted_records)} files."
                    )
                else:
                    # Otherwise, do a full topological sort
                    sorted_records = _topological_sort(all_file_records)
                    self.logger.info(
                        f"Full transitive sort ({len(sorted_records)} files) "
                        f"on project '{project_name}'."
                    )
            else:
                # transitive=False => always a full topological sort
                sorted_records = _topological_sort(all_file_records)
                self.logger.info(
                    f"Non-transitive sort ({len(sorted_records)} files) "
                    f"on project '{project_name}'."
                )

            # ------------------------------------------------------
            # PHASE 3: HANDLE start_file EVEN IF NOT TRANSITIVE
            # (i.e., skip up to that file in the sorted list)
            # ------------------------------------------------------
            if start_file and not transitive:
                # Find the first occurrence of `start_file` by name in the sorted list
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
                # Make sure we do not exceed length
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
        # PHASE 5: PROCESS THE SORTED FILES
        # ------------------------------------------------------
        if not self.dry_run and sorted_records:
            _process_project_files(
                global_attrs=project,
                file_records=sorted_records,
                template_dir=template_dir,  # Each record has its own TEMPLATE_SET
                agent_env=self.agent_env,
                logger=self.logger,
                start_idx=0,
            )
            self.logger.info(f"Completed file generation workflow on '{project_name}'.")

        return (sorted_records, start_idx)
