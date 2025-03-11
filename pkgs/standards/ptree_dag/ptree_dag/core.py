"""
core.py

This module defines the main class for the file generation workflow.
The ProjectFileGenerator class encapsulates the overall workflow:
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
import colorama
from colorama import init as colorama_init, Fore, Back, Style
import os
import yaml
from typing import Any, Dict, List, Optional, Tuple
from pydantic import FilePath

from pathlib import Path

# Import helper modules from our package.
from ._processing import _process_project_files
from ._graph import _topological_sort
from ._Jinja2PromptTemplate import j2pt
from ._config import _config

import ptree_dag.templates
from pydantic import Field, ConfigDict, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base import FullUnion
from swarmauri_standard.logging.Logger import Logger
from swarmauri_base.logging.LoggerBase import LoggerBase

colorama_init(autoreset=True)

class ProjectFileGenerator(ComponentBase):
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
    logger: FullUnion[LoggerBase] = Logger(name=Fore.GREEN + "pfg" + Style.RESET_ALL)
    dry_run: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)
    version: str = "0.1.0"

    @model_validator(mode="after")
    def setup_env(self) -> "ProjectFileGenerator":
        # Gather all physical directories that provide ptree_dag.templates:
        namespace_dirs = list(ptree_dag.templates.__path__)  # installed template dirs
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
            self.logger.info("Loaded " +Fore.GREEN + f"{len(self.projects_list)}" + Style.RESET_ALL + f" projects from '{self.projects_payload_path}'.")
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
        for project in self.projects_list:
            file_records, start_idx = self.process_single_project(project)
            sorted_records.append(file_records)
        return sorted_records


    def process_single_project(self, project: Dict[str, Any], start_idx: int = 0, start_file: Optional[str] = None) -> Tuple[list,int]:
        """
        1) For each package in the project, render its ptree.yaml.j2 to get file records.
        2) Combine those records into a single list.
        3) Perform topological sort across ALL records in the project.
        4) Process the sorted records.
        """

        # We gather all file records from all packages here:
        all_file_records = []

        packages = project.get("PACKAGES", [])
        project_name = project.get("PROJECT_NAME", "UnnamedProject")
        # ------------------------------------------------------
        # PHASE 1: RENDER EACH PACKAGE’S ptree.yaml.j2
        # ------------------------------------------------------
        for pkg in packages:
            project_only_context = project.copy()
            project_only_context['PACKAGES'] = [pkg]


            # 1A. Determine the correct template set for this package
            #     either from an override on the package or from the project-level default
            pkg_template_set = pkg.get("TEMPLATE_SET_OVERRIDE") or pkg.get("TEMPLATE_SET", None) or project.get("TEMPLATE_SET", "default")

            try:
                template_dir = self.get_template_dir_any(pkg_template_set)
                self.update_templates_dir(template_dir)
            except ValueError as e:
                self.logger.error(Fore.GREEN + f"[{project_name}] "+ Style.RESET_ALL + 
                    "Package '{pkg.get('NAME')}' error: {e}")
                continue  # skip or handle differently

            # 1B. Find the package’s `ptree.yaml.j2` in that template directory
            ptree_template_path = os.path.join(template_dir, "ptree.yaml.j2")
            if not os.path.isfile(ptree_template_path):
                self.logger.error(
                    Fore.GREEN + f"[{project_name}] "+ Style.RESET_ALL + 
                    "Missing ptree.yaml.j2 in template dir {template_dir} for package '{pkg.get('NAME')}'."
                )
                continue

            # 1C. Render it with the package data
            try:
                self.j2pt.set_template(FilePath(ptree_template_path))
                rendered_yaml_str = self.j2pt.fill(project_only_context)  # or fill(**pkg)
            except Exception as e:
                self.logger.error(Fore.GREEN + f"[{project_name}] "+ Style.RESET_ALL + 
                    "Render failure for package '{pkg.get('NAME')}': {e}")
                continue

            # 1D. Parse the rendered YAML into file records
            try:
                partial_data = yaml.safe_load(rendered_yaml_str)
            except yaml.YAMLError as e:
                self.logger.error(Fore.GREEN + f"[{project_name}] "+ Style.RESET_ALL + 
                    "YAML parse failure for '{pkg.get('NAME')}': {e}")
                continue

            # 1E. The partial data might be {"FILES": [...]} or just [...]
            if isinstance(partial_data, dict) and "FILES" in partial_data:
                pkg_file_records = partial_data["FILES"]
            elif isinstance(partial_data, list):
                pkg_file_records = partial_data
            else:
                self.logger.warning(
                    Fore.RED + f"[{project_name}] "+ Style.RESET_ALL + 
                    "Unexpected YAML structure from package '{pkg.get('NAME')}'; skipping."
                )
                continue

            # 1F. Set template on each file
            for record in pkg_file_records:
                record.update({"TEMPLATE_SET":template_dir})

            # 1G. Accumulate these package-level file records
            all_file_records.extend(pkg_file_records)

        # ------------------------------------------------------
        # PHASE 2: TOPOLOGICAL SORT ACROSS ALL RECORDS
        # ------------------------------------------------------
        if not all_file_records:
            self.logger.warning(Fore.RED + f"[{project_name}] "+ Style.RESET_ALL + 
                "No file records found at all.")
            return

        try:
            sorted_records = _topological_sort(all_file_records)
            if not start_idx and start_file:
                for _idx, _rec in enumerate(sorted_records):
                    if _rec.get("RENDERED_FILE_NAME") == start_file:
                        start_idx = _idx
            sorted_records = sorted_records[start_idx:]
            self.logger.info(
               "Topologically sorted " + Fore.GREEN + f"{len(sorted_records)}" + Style.RESET_ALL 
               + f" on '{project_name}'"
            )
        except Exception as e:
            self.logger.error(Fore.RED + f"[{project_name}] "+ Style.RESET_ALL + 
                f"Failed to topologically sort: {e}")
            return

        # ------------------------------------------------------
        # PHASE 3: PROCESS THE SORTED FILES
        # ------------------------------------------------------
        # If each record might still have a unique template set, you can do a 
        # second override resolution here if needed. Or you can assume the record 
        # already includes its final template path from the partial step.
        if not self.dry_run:
            _process_project_files(
                global_attrs=project,
                file_records=sorted_records,
                # You might pass a default template_dir, but each record can override
                # as needed if your _process_project_files supports that.
                template_dir=template_dir, 
                agent_env=self.agent_env,
                logger=self.logger,
                start_idx=start_idx
            )
            self.logger.info(f"Completed file generation workflow on {project_name}'")
            return sorted_records, start_idx
        else:
            return sorted_records, start_idx


