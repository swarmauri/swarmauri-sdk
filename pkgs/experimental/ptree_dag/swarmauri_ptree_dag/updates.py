"""
updates.py

This module provides functions for updating and saving configuration data.
It is organized into two sections:

Section 1: Global Projects YAML CRUD Operations
  - These functions update the in‑memory global projects data that mirror the structure
    of your global YAML file (e.g. projects_payload.yaml).
  - They include methods for updating top-level keys, package‑level keys, and module‑level keys,
    with support for list-based updates (replace, append, remove).
  - The save_global_projects() function writes the updated data back to the global YAML file.

Section 2: Template (.yaml.j2) CRUD Operations
  - These functions perform CRUD operations on the in‑memory representation of your template.
  - They let you add, update, or remove file records (and other entities) from the template.
  - The save_template() function writes the updated template data back to the .yaml.j2 file.
"""

import os
import yaml
from typing import Any, Dict

# -----------------------------------------------------------------------------
# Section 1: Global Projects YAML CRUD Operations
# -----------------------------------------------------------------------------

# Global in‑memory representation of your projects data.
GLOBAL_PROJECTS_DATA: Dict[str, Any] = {}


def update_global_value(key: str, value: Any) -> None:
    """
    Updates a top-level key in the in‑memory global projects data.

    Parameters:
      key (str): The key to update.
      value (Any): The new value to assign.
    """
    GLOBAL_PROJECTS_DATA[key] = value
    print(f"[INFO] Global value updated: {key} = {value}")


def update_package_value(project_name: str, package_name: str, key: str, new_value: Any, mode: str = "replace") -> bool:
    """
    Updates a key value for a specific package within a given project in the global projects data.
    Supports list operations via the mode parameter:
      - "replace": Replace the entire value.
      - "append": Append (or extend) if the current value is a list.
      - "remove": Remove items from a list if applicable.
    
    Parameters:
      project_name (str): The name of the project (e.g. "tooling").
      package_name (str): The name of the package.
      key (str): The package-level key to update.
      new_value (Any): The new value or values.
      mode (str): Operation mode ("replace", "append", or "remove"). Defaults to "replace".
    
    Returns:
      bool: True if update successful, False otherwise.
    """
    updated = False
    projects = GLOBAL_PROJECTS_DATA.get("PROJECTS", [])
    for project in projects:
        if project.get("NAME") == project_name:
            for pkg in project.get("PACKAGES", []):
                if pkg.get("NAME") == package_name:
                    current_value = pkg.get(key)
                    if isinstance(current_value, list):
                        if mode == "append":
                            if isinstance(new_value, list):
                                pkg[key] = current_value + new_value
                            else:
                                current_value.append(new_value)
                        elif mode == "remove":
                            if isinstance(new_value, list):
                                pkg[key] = [item for item in current_value if item not in new_value]
                            else:
                                pkg[key] = [item for item in current_value if item != new_value]
                        else:  # "replace"
                            pkg[key] = new_value
                    else:
                        pkg[key] = new_value
                    updated = True
                    print(f"[INFO] Updated package '{package_name}' key '{key}' to '{pkg[key]}' (mode: {mode}) in project '{project_name}'.")
                    break
            if not updated:
                print(f"[WARNING] Package '{package_name}' not found in project '{project_name}'.")
            break
    else:
        print(f"[WARNING] Project '{project_name}' not found in global projects data.")
    return updated


def update_module_value(project_name: str, package_name: str, module_name: str, key: str, new_value: Any, mode: str = "replace") -> bool:
    """
    Updates a key value for a specific module within a package in the global projects data.
    Supports list operations via the mode parameter:
      - "replace": Replace the entire value.
      - "append": Append (or extend) if the current value is a list.
      - "remove": Remove items from a list if applicable.
    
    Parameters:
      project_name (str): The name of the project.
      package_name (str): The name of the package.
      module_name (str): The name of the module.
      key (str): The module-level key to update.
      new_value (Any): The new value or values.
      mode (str): Operation mode ("replace", "append", or "remove"). Defaults to "replace".
    
    Returns:
      bool: True if update successful; False otherwise.
    """
    updated = False
    projects = GLOBAL_PROJECTS_DATA.get("PROJECTS", [])
    for project in projects:
        if project.get("NAME") == project_name:
            for pkg in project.get("PACKAGES", []):
                if pkg.get("NAME") == package_name:
                    for mod in pkg.get("MODULES", []):
                        if mod.get("NAME") == module_name:
                            current_value = mod.get(key)
                            if isinstance(current_value, list):
                                if mode == "append":
                                    if isinstance(new_value, list):
                                        mod[key] = current_value + new_value
                                    else:
                                        current_value.append(new_value)
                                elif mode == "remove":
                                    if isinstance(new_value, list):
                                        mod[key] = [item for item in current_value if item not in new_value]
                                    else:
                                        mod[key] = [item for item in current_value if item != new_value]
                                else:  # "replace"
                                    mod[key] = new_value
                            else:
                                mod[key] = new_value
                            updated = True
                            print(f"[INFO] Updated module '{module_name}' key '{key}' to '{mod[key]}' (mode: {mode}) in package '{package_name}' of project '{project_name}'.")
                            break
                    if not updated:
                        print(f"[WARNING] Module '{module_name}' not found in package '{package_name}'.")
                    break
            break
    if not updated:
        print(f"[WARNING] Could not update module value. Please verify the project/package/module names.")
    return updated


def save_global_projects(global_projects_path: str) -> None:
    """
    Saves the in‑memory global projects data back to the specified global YAML file.

    Parameters:
      global_projects_path (str): Path to the global projects YAML file (e.g. projects_payload.yaml).
    """
    try:
        with open(global_projects_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(GLOBAL_PROJECTS_DATA, f, default_flow_style=False, sort_keys=False)
        print(f"[INFO] Global projects saved to: {global_projects_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save global projects: {e}")

# -----------------------------------------------------------------------------
# Section 2: Template (.yaml.j2) CRUD Operations
# -----------------------------------------------------------------------------

# Global in‑memory representation of your template data.
TEMPLATE_DATA: Dict[str, Any] = {}


def update_template(operation: str, target: str, data: Dict[str, Any]) -> None:
    """
    Performs a CRUD operation on the in‑memory template data.
    
    Parameters:
      operation (str): The operation to perform ("add", "update", "remove").
      target (str): The target entity in the template (e.g. "project", "package", "module", "file", or "dependency").
      data (Dict[str, Any]): Data required to perform the operation.
         For "add", this might be a new file record; for "update", an identifier and updated fields;
         for "remove", an identifier.
    """
    global TEMPLATE_DATA

    if operation == "add":
        if target == "file":
            TEMPLATE_DATA.setdefault("FILES", []).append(data)
            print(f"[INFO] Added new file record to template: {data}")
        elif target == "dependency":
            TEMPLATE_DATA.setdefault("DEPENDENCIES", []).append(data)
            print(f"[INFO] Added new dependency to template: {data}")
        # Extend for other targets as needed.
    elif operation == "update":
        if target == "file":
            file_id = data.get("id")
            updated = False
            for record in TEMPLATE_DATA.get("FILES", []):
                if record.get("id") == file_id:
                    record.update(data)
                    updated = True
                    print(f"[INFO] Updated file record with id {file_id}")
                    break
            if not updated:
                print(f"[WARNING] File record with id {file_id} not found for update.")
        # Extend for other targets as needed.
    elif operation == "remove":
        if target == "file":
            file_id = data.get("id")
            original_count = len(TEMPLATE_DATA.get("FILES", []))
            TEMPLATE_DATA["FILES"] = [r for r in TEMPLATE_DATA.get("FILES", []) if r.get("id") != file_id]
            if len(TEMPLATE_DATA["FILES"]) < original_count:
                print(f"[INFO] Removed file record with id {file_id}")
            else:
                print(f"[WARNING] File record with id {file_id} not found for removal.")
        # Extend for other targets as needed.
    else:
        print(f"[ERROR] Unknown operation '{operation}' for update_template.")


def save_template(template_file_path: str) -> None:
    """
    Saves the in‑memory template data back to the specified .yaml.j2 file.

    Parameters:
      template_file_path (str): Path to the template (.yaml.j2) file.
    """
    try:
        with open(template_file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(TEMPLATE_DATA, f, default_flow_style=False, sort_keys=False)
        print(f"[INFO] Template saved to: {template_file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save template: {e}")
