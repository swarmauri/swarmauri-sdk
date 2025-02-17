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
from jinja2 import Environment, FileSystemLoader
from typing import Any, Dict, List, Optional, Union
from pydantic import FilePath
from pprint import pprint

# Import helper modules from our package.
from .rendering import _render_project_yaml, _render_field
from .processing import process_project_files
from .graph import _build_forward_graph, _topological_sort, _find_start_node, _process_from_node
from .updates import update_global_value, update_package_value, update_module_value, save_global_projects, update_template, save_template, GLOBAL_PROJECTS_DATA
from .dependencies import get_direct_dependencies, get_transitive_dependencies, get_dependents, resolve_glob_dependencies
from .external import call_external_agent, chunk_content
from .Jinja2PromptTemplate import Jinja2PromptTemplate, j2pt


class ProjectFileGenerator:
    """
    Encapsulates the file generation workflow for projects defined in a global YAML.
    Supports operations such as:
      - Loading projects.
      - Processing all projects or a single project.
      - Starting processing from an arbitrary file (via dependency graph ordering).
      - Querying dependencies and dependents.
      - Updating and saving configuration in both the global projects YAML and the template (.yaml.j2) file.
    """

    def __init__(self, 
                 projects_payload_path: str, 
                 template_base_dir: Union[str, FilePath],  
                 agent_env: Optional[Dict[str, Any]] = None,
                 prompt_template_engine: Jinja2PromptTemplate = j2pt):
        """
        Initialize a new ProjectFileGenerator instance.

        Parameters:
          projects_payload_path (str): Path to the global projects YAML file (e.g. "projects_payload.yaml").
          template_base_dir (str): Base directory for the template sets (e.g. "./templatesv2").
          agent_env (dict, optional): Configuration for the external agent (if using GENERATE process).
        """
        self.projects_payload_path = projects_payload_path
        self.base_dir = os.getcwd()  # Current working directory
        self.swarmauri_package_path = os.path.join("e:\\swarmauri_github\\swarmauri-sdk\\pkgs")
        self.template_base_dir = template_base_dir
        self.j2pt = prompt_template_engine
        self.agent_env = agent_env if agent_env is not None else {}
        self.projects_list: List[Dict[str, Any]] = []
        # Optionally, dependency graph attributes (built per project)
        self.dependency_graph: Dict[str, List[str]] = {}
        self.in_degree: Dict[str, int] = {}
        # Set up a Jinja2 environment for "COPY" operations.
        self.copy_env = Environment(loader=FileSystemLoader([template_base_dir, os.getcwd()]), autoescape=False)
        self.j2pt.templates_dir = [self.base_dir, self.swarmauri_package_path, self.template_base_dir]

    # ---------------------
    # J2PT Methods
    # ---------------------

    def update_templates_dir(self, package_specific_template_dir):
        self.j2pt.templates_dir = [self.base_dir, 
                                   self.swarmauri_package_path,
                                   package_specific_template_dir]
        
        
    def get_template_dir_any(self, template_set: str) -> str:
        # Use the provided template_base_dir as the base directory.
        template_dir = os.path.join(os.path.abspath(self.template_base_dir), template_set)
        if not os.path.isdir(template_dir):
            raise ValueError(
                f"Template directory '{template_set}' does not exist in {self.template_base_dir}."
            )
        return template_dir
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
            print(f"[INFO] Loaded {len(self.projects_list)} projects from '{self.projects_payload_path}'.")
        except Exception as e:
            print(f"[ERROR] Failed to load projects: {e}")
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
            print(f"[ERROR] {e}")
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
            print(f"[INFO] Topologically sorted {len(sorted_records)} file records for project '{project.get('PROJECT_NAME')}'.")
        except Exception as e:
            print(f"[ERROR] Failed to sort file records for project '{project.get('PROJECT_NAME')}': {e}")
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
            print(f"[ERROR] The file {path} does not exist.")
            return []
        except yaml.YAMLError as e:
            print(f"[ERROR] Failed to parse rendered YAML from {path}: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred while loading files payload: {e}")
            return []