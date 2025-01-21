#!/usr/bin/env python3
"""
pyproject_ops.py

Provides functions for operating on pyproject.toml files:
  - extract_path_dependencies: Retrieves dependencies that are defined with a "path".
  - extract_git_dependencies: Retrieves dependencies that are defined with a "git" key.
  - update_dependency_versions: For local dependencies (with a "path"), update their version in the parent 
    pyproject.toml and optionally in the dependency’s own pyproject.toml.

These functions can be used independently or integrated into a larger monorepo management tool.
"""

import os
import sys
import toml


def extract_path_dependencies(pyproject_path):
    """
    Extract local (path) dependencies from a pyproject.toml file.

    Looks for dependencies in [tool.poetry.dependencies] that are dictionaries containing a "path" key.

    Args:
        pyproject_path (str): Path to the pyproject.toml file.

    Returns:
        list: A list of path strings extracted from the dependency definitions.
    """
    try:
        with open(pyproject_path, "r") as f:
            data = toml.load(f)
    except Exception as e:
        print(f"Error reading {pyproject_path}: {e}", file=sys.stderr)
        sys.exit(1)

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    path_deps = [
        value["path"]
        for value in dependencies.values()
        if isinstance(value, dict) and "path" in value
    ]
    return path_deps


def extract_git_dependencies(pyproject_path):
    """
    Extract Git-based dependencies from a pyproject.toml file.

    Looks for dependencies in [tool.poetry.dependencies] that are dictionaries containing a "git" key.

    Args:
        pyproject_path (str): Path to the pyproject.toml file.

    Returns:
        dict: A dictionary mapping dependency names to their details dictionaries.
    """
    try:
        with open(pyproject_path, "r") as f:
            data = toml.load(f)
    except Exception as e:
        print(f"Error reading {pyproject_path}: {e}", file=sys.stderr)
        sys.exit(1)

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    git_deps = {
        name: details
        for name, details in dependencies.items()
        if isinstance(details, dict) and "git" in details
    }
    return git_deps


def update_dependency_versions(pyproject_path, new_version):
    """
    Update versions for local (path) dependencies in a pyproject.toml file.

    For each dependency that is defined as a table with a "path" key:
      - The dependency’s version is updated to f"^{new_version}" in the parent pyproject.toml.
      - Attempts to update the dependency's own pyproject.toml (if found in the given path)
        by setting its version to new_version.

    Args:
        pyproject_path (str): Path to the parent pyproject.toml file.
        new_version (str): The new version string to set (without the caret).

    Returns:
        None
    """
    try:
        with open(pyproject_path, "r") as f:
            data = toml.load(f)
    except Exception as e:
        print(f"Error reading {pyproject_path}: {e}", file=sys.stderr)
        sys.exit(1)

    poetry_section = data.get("tool", {}).get("poetry", {})
    dependencies = poetry_section.get("dependencies", {})
    updated_deps = {}
    base_dir = os.path.dirname(pyproject_path)

    for dep_name, details in dependencies.items():
        if isinstance(details, dict) and "path" in details:
            # Create a new dependency definition with an updated version.
            new_dep = {"version": f"^{new_version}"}
            # Preserve any additional keys (except we override version).
            for key, value in details.items():
                if key != "path":
                    new_dep[key] = value
            updated_deps[dep_name] = new_dep

            # Attempt to update the dependency's own pyproject.toml (if it exists).
            dependency_path = os.path.join(base_dir, details["path"])
            dependency_pyproject = os.path.join(dependency_path, "pyproject.toml")
            if os.path.isfile(dependency_pyproject):
                try:
                    with open(dependency_pyproject, "r") as dep_file:
                        dep_data = toml.load(dep_file)
                    if "tool" in dep_data and "poetry" in dep_data["tool"]:
                        dep_data["tool"]["poetry"]["version"] = new_version
                        with open(dependency_pyproject, "w") as dep_file:
                            toml.dump(dep_data, dep_file)
                        print(f"Updated {dependency_pyproject} to version {new_version}")
                    else:
                        print(f"Invalid structure in {dependency_pyproject}", file=sys.stderr)
                except Exception as e:
                    print(f"Error updating {dependency_pyproject}: {e}", file=sys.stderr)
        else:
            updated_deps[dep_name] = details

    # Write the updated dependencies back to the parent pyproject.toml.
    data["tool"]["poetry"]["dependencies"] = updated_deps
    try:
        with open(pyproject_path, "w") as f:
            toml.dump(data, f)
        print(f"Updated dependency versions in {pyproject_path}")
    except Exception as e:
        print(f"Error writing updated file {pyproject_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Provides a basic CLI for testing pyproject.toml operations.
    
    Usage Examples:
      - Extract dependencies:
            python pyproject_ops.py --pyproject path/to/pyproject.toml
      - Update dependency versions (for local path dependencies):
            python pyproject_ops.py --pyproject path/to/pyproject.toml --update-version 2.0.0
    """
    import argparse

    parser = argparse.ArgumentParser(description="Operate on pyproject.toml dependencies")
    parser.add_argument(
        "--pyproject",
        required=True,
        help="Path to the pyproject.toml file",
    )
    parser.add_argument(
        "--update-version",
        help="If provided, update local dependencies to this version",
    )
    args = parser.parse_args()

    print("Extracting local (path) dependencies:")
    paths = extract_path_dependencies(args.pyproject)
    if paths:
        print(", ".join(paths))
    else:
        print("No path dependencies found.")

    print("\nExtracting Git dependencies:")
    git_deps = extract_git_dependencies(args.pyproject)
    if git_deps:
        for name, details in git_deps.items():
            print(f"{name}: {details}")
    else:
        print("No Git dependencies found.")

    if args.update_version:
        print(f"\nUpdating dependency versions to {args.update_version} ...")
        update_dependency_versions(args.pyproject, args.update_version)


if __name__ == "__main__":
    main()
