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

import os
import yaml
import copy
from typing import Any, Dict, List, Optional, Union
from pydantic import FilePath
from pprint import pprint

from pathlib import Path

# Import helper modules from our package.
from .processing import process_project_files
from .graph import _build_forward_graph, _topological_sort, _find_start_node, _process_from_node
from .updates import update_global_value, update_package_value, update_module_value, save_global_projects, update_template, save_template, GLOBAL_PROJECTS_DATA
from .dependencies import get_direct_dependencies, get_transitive_dependencies, get_dependents, resolve_glob_dependencies
from .external import call_external_agent, chunk_content
from .Jinja2PromptTemplate import Jinja2PromptTemplate, j2pt

import ptree_dag.templates
from pydantic import Field, ConfigDict, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base import FullUnion
from swarmauri_standard.logging.Logger import Logger
from swarmauri_base.logging.LoggerBase import LoggerBase

class ProjectFileGenerator(ComponentBase):
    projects_payload_path: str
    template_base_dir: Optional[str] = None
    agent_env: Dict[str, Any] = Field(default_factory=dict)
    j2pt: Any = Field(default_factory=lambda: j2pt)  # adjust type as needed

    # Derived attributes with default factories:
    base_dir: str = Field(exclude=True, default_factory=os.getcwd)
    additional_package_dirs: List[str] = Field(exclude=True, default=list)
    projects_list: List[Dict[str, Any]] = Field(exclude=True, default_factory=list)
    dependency_graph: Dict[str, List[str]] = Field(exclude=True, default_factory=dict)
    in_degree: Dict[str, int] = Field(exclude=True, default_factory=dict)
    
    # These will be computed in the validator:
    namespace_dirs: List[str] = Field(default_factory=list)
    logger: FullUnion[LoggerBase] = Logger()

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
            self.logger.info(f" Loaded {len(self.projects_list)} projects from '{self.projects_payload_path}'.")
        except Exception as e:
            self.logger.error(f"Failed to load projects: {e}")
            self.projects_list = []
        return self.projects_list

    def process_all_projects(self) -> None:
        """
        Processes all projects in self.projects_list.
        For each project, it renders the project YAML, processes file records,
        and (optionally) handles dependency ordering.
        """
        if not self.projects_list:
            self.load_projects()
        for project in self.projects_list:
            self.process_single_project(project)

    def process_single_project(self, project: Dict[str, Any]) -> None:
        """
        Processes a single project:
          - Renders the project YAML using the .yaml.j2 template from the appropriate template set.
          - Expands file records (package and module context).
          - Builds and orders the dependency graph.
          - Processes all file records (via COPY or GENERATE operations).

        Parameters:
          project (dict): A project dictionary from self.projects_list.
        """
        # Get the template set from the project payload (or use "default")
        template_set = project.get("TEMPLATE_SET", "default")
        try:
            template_dir = self.get_template_dir_any(template_set)
            self.update_templates_dir(template_dir)
        except ValueError as e:
            self.logger.error(f"{e}")
            return
    
        # Note: Use the YAML version of the payload template.
        files_payload_template_path = os.path.join(template_dir, "ptree.yaml.j2")
        # Step 1: Load the files payload using the YAML payload template
        files_payload = self.load_files_payload(files_payload_template_path, project)
        
        # Optionally, build the dependency graph (if your workflow requires it).
        try:
            sorted_records = _topological_sort(files_payload)
            
            import json
            with open('sorted_records.json', 'w') as f:
                json.dump(sorted_records, f, indent=4)
            self.logger.info(f" Topologically sorted {len(sorted_records)} file records for project '{project.get('PROJECT_NAME')}'.")
        except Exception as e:
            self.logger.error(f"Failed to sort file records for project '{project.get('PROJECT_NAME')}': {e}")
            sorted_records = file_records

        # Process the file records.
        process_project_files(global_attrs=project, 
                              file_records=sorted_records, 
                              template_dir=template_dir, 
                              agent_env =self.agent_env)

    def load_files_payload(self, path, global_attrs):
        """
        Loads a Jinja2-based YAML template (payload.yaml.j2), renders it
        with `global_attrs`, and then parses the result as YAML.
        
        Supports an optional top-level key "AGENT_PROMPT_TEMPLATE" in the payload.
        If the rendered YAML is a dictionary, it is expected to contain a "FILES"
        key with the list of file payloads, and optionally an "AGENT_PROMPT_TEMPLATE".
        If the rendered YAML is a list, then it is taken as the list of file payloads.
        """
        try:
            ## use j2pt to render the ptree.yaml.j2
            self.logger.info(path)
            self.j2pt.set_template(FilePath(path))

            rendered_str = self.j2pt.fill(global_attrs)

            with open('dump.yaml', 'w') as f:
                 f.writelines(rendered_str)

            payload_data = yaml.safe_load(rendered_str)
            
            if isinstance(payload_data, dict):
                # If an agent prompt template is defined in the payload, update global_attrs.
                if "AGENT_PROMPT_TEMPLATE" in payload_data:
                    global_attrs["AGENT_PROMPT_TEMPLATE"] = payload_data["AGENT_PROMPT_TEMPLATE"]
                # Return the list of file definitions under the "FILES" key.
                return payload_data.get("FILES", [])
            else:
                # If the payload is a list, return it as is.
                return payload_data
        except FileNotFoundError:
            self.logger.error(f"The file {path} does not exist.")
            return []
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse rendered YAML from {path}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading files payload: {e}")
            return []