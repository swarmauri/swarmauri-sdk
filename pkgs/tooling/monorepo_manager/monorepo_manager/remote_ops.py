#!/usr/bin/env python3
"""
remote_ops.py

Provides functions to:
  - Fetch the version from a remote GitHub repository's pyproject.toml.
  - Update a local pyproject.toml by resolving Git dependencies:
      - For dependencies defined with a 'git' key,
      - Replace their version with an inline table containing the fetched version,
      - Mark dependencies as optional.
  - Write the updated pyproject.toml to a file (or overwrite the input file).
  
Intended for use in a unified monorepo management CLI.
"""

from urllib.parse import urljoin

import requests
from tomlkit import parse, dumps, inline_table


def fetch_remote_pyproject_version(git_url, branch="main", subdirectory=""):
    """
    Fetches the version string from a remote pyproject.toml in a GitHub repository.

    Args:
        git_url (str): The Git repository URL (must be a GitHub URL).
        branch (str): The branch to fetch the file from (default: "main").
        subdirectory (str): The subdirectory in the repo where the pyproject.toml is located (if any).

    Returns:
        str or None: The version string if found, otherwise None.
    """
    try:
        if "github.com" not in git_url:
            raise ValueError("Only GitHub repositories are supported by this function.")
        
        # Remove trailing .git if present.
        repo_path = git_url.split("github.com/")[1]
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]
        
        # Build the raw URL; ensure subdirectory ends with "/" if provided.
        base_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/"
        if subdirectory and not subdirectory.endswith("/"):
            subdirectory += "/"
        pyproject_url = urljoin(base_url, f"{subdirectory}pyproject.toml")
        
        response = requests.get(pyproject_url)
        response.raise_for_status()
        doc = parse(response.text)
        version = doc.get("tool", {}).get("poetry", {}).get("version")
        if version is None:
            print(f"Version key not found in remote pyproject.toml from {pyproject_url}")
        return version
    except Exception as e:
        print(f"Error fetching pyproject.toml from {git_url}: {e}")
        return None


def update_pyproject_with_versions(file_path):
    """
    Reads the local pyproject.toml file and updates Git-based dependencies.
    
    For dependencies defined as a table with a 'git' key, it:
      - Fetches the version from the remote repository.
      - Creates an inline table for the dependency with the resolved version (prefixed with '^').
      - Marks the dependency as optional.
    Also ensures that dependencies referenced in extras are marked as optional.
    
    Args:
        file_path (str): Path to the local pyproject.toml file.
    
    Returns:
        tomlkit.document.Document: The updated TOML document.
        If an error occurs, prints the error and returns None.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
        doc = parse(content)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    try:
        tool_section = doc["tool"]
        poetry_section = tool_section["poetry"]
    except KeyError:
        print(f"Error: Invalid pyproject.toml structure in {file_path}.", flush=True)
        return None

    dependencies = poetry_section.get("dependencies", {})
    extras = poetry_section.get("extras", {})

    for dep_name, details in dependencies.items():
        # Process only Git-based dependencies.
        if isinstance(details, dict) and "git" in details:
            git_url = details["git"]
            branch = details.get("branch", "main")
            subdirectory = details.get("subdirectory", "")
            print(f"Updating dependency '{dep_name}':")
            print(f"  Repository: {git_url}")
            print(f"  Branch: {branch}")
            print(f"  Subdirectory: {subdirectory}")
            remote_version = fetch_remote_pyproject_version(git_url, branch=branch, subdirectory=subdirectory)
            if remote_version:
                print(f"  Fetched version: {remote_version}")
                # Create an inline table with the resolved version and mark as optional.
                dep_inline = inline_table()
                dep_inline["version"] = f"^{remote_version}"
                dep_inline["optional"] = True
                dependencies[dep_name] = dep_inline
            else:
                print(f"  Could not fetch remote version for '{dep_name}'. Marking as optional.")
                # Mark as optional if version could not be fetched.
                details["optional"] = True
                dependencies[dep_name] = details
        else:
            # If the dependency appears in extras but is just a string, convert it to an inline table and mark as optional.
            for extra_name, extra_deps in extras.items():
                if dep_name in extra_deps:
                    if isinstance(details, str):
                        dep_inline = inline_table()
                        dep_inline["version"] = details
                        dep_inline["optional"] = True
                        dependencies[dep_name] = dep_inline
                    elif isinstance(details, dict):
                        details["optional"] = True
                    break  # Only need to update once.

    # Clean the extras section: ensure each extra only contains dependencies that exist.
    for extra_name, extra_deps in extras.items():
        extras[extra_name] = [dep for dep in extra_deps if dep in dependencies]

    # Update the document.
    poetry_section["dependencies"] = dependencies
    poetry_section["extras"] = extras
    return doc


def update_and_write_pyproject(input_file_path, output_file_path=None):
    """
    Updates the specified pyproject.toml file with resolved versions for Git-based dependencies 
    and writes the updated document to a file.
    
    Args:
        input_file_path (str): Path to the original pyproject.toml file.
        output_file_path (str, optional): Path to write the updated file.
                                        If not provided, the input file is overwritten.
    
    Returns:
        bool: True if the update and write succeed, False otherwise.
    """
    updated_doc = update_pyproject_with_versions(input_file_path)
    if updated_doc is None:
        print("Failed to update the pyproject.toml document.")
        return False

    # Overwrite input file if output file not provided.
    output_file_path = output_file_path or input_file_path

    try:
        with open(output_file_path, "w") as f:
            f.write(dumps(updated_doc))
        print(f"Updated pyproject.toml written to {output_file_path}")
        return True
    except Exception as e:
        print(f"Error writing updated pyproject.toml: {e}")
        return False


# Example usage when running this module directly.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Update local pyproject.toml with versions fetched from Git dependencies."
    )
    parser.add_argument("--input", required=True, help="Path to the local pyproject.toml to update")
    parser.add_argument("--output", help="Optional output file path (if not specified, overwrites input)")
    args = parser.parse_args()

    success = update_and_write_pyproject(args.input, args.output)
    if not success:
        exit(1)
