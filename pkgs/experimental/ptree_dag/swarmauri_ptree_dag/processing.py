"""
processing.py

This module contains functions for processing file records within a project.
It supports processing each individual file based on its PROCESS_TYPE:
  - For "COPY": It renders the file’s template using the provided context.
  - For "GENERATE": It renders an agent prompt template, calls an external agent to generate content,
    and then saves the generated content.
The module also provides a function to process all file records for a project.
"""

import os
from typing import Dict, Any, List
from jinja2 import Environment
from .rendering import _render_copy_template, _render_generate_template, _render_field

# If needed, you could also import additional functions such as chunk_content from external.py.
# from filegenerator.external import chunk_content


def _save_file(content: str, filepath: str) -> None:
    """
    Saves the given content to the specified file path.
    Creates the target directory if it does not exist.

    Parameters:
      content (str): The file content to save.
      filepath (str): The full path (including file name) where the content should be saved.
    """
    try:
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] File saved: {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to save file '{filepath}': {e}")


def _create_context(file_record, project_global_attributes):
    project_name = file_record.get('PROJECT_NAME')
    package_name = file_record.get('PACKAGE_NAME')
    module_name = file_record.get('MODULE_NAME')

    # Initialize the context
    context = {}

    # Find the project information
    if project_name:
        project = project_global_attributes  # project_global_attributes contains all the project context
        context['PROJECT'] = project

    # If a package_name is provided, match it to the correct package
    if package_name:
        package = next((pkg for pkg in project_global_attributes['PACKAGES'] if pkg['NAME'] == package_name), None)
        if package:
            context['PKG'] = package

    # If a module_name is provided, match it to the correct module within the package
    if module_name:
        module = None
        if package_name:
            print(package_name)
            package = next((pkg for pkg in project_global_attributes['PACKAGES'] if pkg['NAME'] == package_name), None)
            if package:
                module = next((mod for mod in package['MODULES'] if mod['NAME'] == module_name), None)
        if module:
            context['MOD'] = module
    
    # If the file is package-level or module-level, add the corresponding modules
    if package_name and package:
        context['MODULES'] = [mod for mod in package['MODULES']]
       
    context = {**context, **file_record}
    return context

def _process_file(file_record: Dict[str, Any],
                  global_attrs: Dict[str, Any],
                  template_dir: str,
                  agent_env: Dict[str, Any]) -> None:
    """
    Processes a single file record based on its PROCESS_TYPE.

    For a "COPY" process, the function renders the file’s template using the copy environment.
    For a "GENERATE" process, the function renders an agent prompt template and calls an external
    agent to generate content.

    Parameters:
      file_record (dict): The file record containing necessary fields (e.g., FILE_NAME, PROCESS_TYPE).
      global_attrs (dict): The project-level context.
      template_dir (str): The base directory where template files reside.
      agent_env (dict): Configuration for agent operations (used in GENERATE process).
    """
    # Merge the project-level context with file-specific data.
    context = _create_context(file_record, global_attrs)
    # from pprint import pprint

    # print("_process_file: combined context")
    # pprint(context)
    # print('\n\n')
    
    # Render the file name field (which might still be unresolved) to determine the target file path.
    final_filename = file_record.get("RENDERED_FILE_NAME")
    
    process_type = file_record.get("PROCESS_TYPE", "COPY").upper()
    
    if process_type == "COPY":
        content = _render_copy_template(file_record, context)
    elif process_type == "GENERATE":
        # Determine the agent prompt template.
        agent_prompt_template_name = file_record.get("AGENT_PROMPT_TEMPLATE", "agent_default.j2")
        agent_prompt_template_path = os.path.join(template_dir, agent_prompt_template_name)
        content = _render_generate_template(file_record, context, agent_prompt_template_path, agent_env)
    else:
        print(f"[WARNING] Unknown PROCESS_TYPE '{process_type}' for file '{final_filename}'. Skipping.")
        return

    _save_file(content, final_filename)
        
    if not content:
        print(f"[WARNING] No content generated for file '{final_filename}'.")


def process_project_files(global_attrs: Dict[str, Any],
                          file_records: List[Dict[str, Any]],
                          template_dir: str,
                          agent_env: Dict[str, Any]) -> None:
    """
    Processes all file records for a project.

    Iterates over each file record and processes it using the appropriate method based on the file's PROCESS_TYPE.
    This function is typically called after the file records have been expanded to include package and module contexts.

    Parameters:
      global_attrs (dict): The project-level context.
      file_records (list of dict): A list of file records to process.
      template_dir (str): The base directory for templates.
      agent_env (dict): Configuration for agent operations used in GENERATE processing.
    """
    for file_record in file_records:
        _process_file(file_record, global_attrs, template_dir, agent_env)
