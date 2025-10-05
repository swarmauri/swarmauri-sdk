import requests
from tomlkit import parse, dumps, inline_table
from urllib.parse import urljoin


def fetch_remote_pyproject_version(git_url, branch="master", subdirectory=""):
    """
    Fetch the version from a remote pyproject.toml file in a GitHub repository.

    Args:
        git_url (str): The Git repository URL.
        branch (str): The branch to fetch from.
        subdirectory (str): The subdirectory where the pyproject.toml resides.

    Returns:
        str: The version string if found, otherwise None.
    """
    try:
        if "github.com" not in git_url:
            raise ValueError("Only GitHub repositories are supported in this script.")

        # Remove trailing .git if present.
        repo_path = git_url.split("github.com/")[1]
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]

        # Build the raw URL.
        base_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/"
        if subdirectory and not subdirectory.endswith("/"):
            subdirectory += "/"
        pyproject_url = urljoin(base_url, f"{subdirectory}pyproject.toml")

        response = requests.get(pyproject_url)
        response.raise_for_status()
        doc = parse(response.text)
        version = doc.get("tool", {}).get("poetry", {}).get("version")
        return version

    except Exception as e:
        print(f"Error fetching pyproject.toml from {git_url}: {e}")
        return None


def update_pyproject_with_versions(file_path):
    """
    Read the local pyproject.toml, update versions for Git dependencies (including extras),
    and ensure dependencies referenced in extras are marked as optional.

    Args:
        file_path (str): Path to the local pyproject.toml file.

    Returns:
        A tomlkit Document with updated dependency information, or None on error.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
        doc = parse(content)
        deps = doc["tool"]["poetry"]["dependencies"]
        extras = doc["tool"]["poetry"].get("extras", {})

        for dep_name, details in deps.items():
            # Check if the dependency is a table (dict-like) with a 'git' key.
            if isinstance(details, dict) and "git" in details:
                git_url = details["git"]
                branch = details.get("branch", "master")
                subdirectory = details.get("subdirectory", "")

                print(f"Updating dependency: {dep_name}")
                print(f"  Repository: {git_url}")
                print(f"  Branch: {branch}")
                print(f"  Subdirectory: {subdirectory}")

                version = fetch_remote_pyproject_version(
                    git_url, branch=branch, subdirectory=subdirectory
                )
                if version:
                    print(f"  Found version: {version}")
                    # Create an inline table for the dependency using inline_table()
                    inline_dep = inline_table()
                    inline_dep["version"] = f"^{version}"
                    inline_dep["optional"] = True
                    deps[dep_name] = inline_dep
                else:
                    print(f"  Failed to fetch version for {dep_name}")
                    details["optional"] = True
            else:
                # For non-Git dependencies referenced in extras,
                # if it's a simple string, convert it to an inline table.
                for extra_name, extra_deps in extras.items():
                    if dep_name in extra_deps:
                        if isinstance(details, str):
                            inline_dep = inline_table()
                            inline_dep["version"] = details
                            inline_dep["optional"] = True
                            deps[dep_name] = inline_dep
                        elif isinstance(details, dict):
                            details["optional"] = True

        # Clean extras: ensure each extra's list references valid dependencies.
        for extra_name, extra_deps in extras.items():
            extras[extra_name] = [dep for dep in extra_deps if dep in deps]

        return doc
    except Exception as e:
        print(f"Error reading or updating pyproject.toml: {e}")
        return None


def update_and_write_pyproject(input_file_path, output_file_path=None):
    """
    Updates the specified pyproject.toml file with resolved versions for Git dependencies
    and writes the updated document to a file.

    Args:
        input_file_path (str): Path to the original pyproject.toml file.
        output_file_path (str, optional): Path to write the updated file. If not specified,
                                          the input file will be overwritten.

    Returns:
        True if the update and write succeed, False otherwise.
    """
    updated_doc = update_pyproject_with_versions(input_file_path)
    if updated_doc is None:
        print("Failed to update the pyproject.toml document.")
        return False

    # If no output path is provided, overwrite the input file.
    if output_file_path is None:
        output_file_path = input_file_path

    try:
        with open(output_file_path, "w") as f:
            f.write(dumps(updated_doc))
        print(f"Updated pyproject.toml written to {output_file_path}")
        return True
    except Exception as e:
        print(f"Error writing updated pyproject.toml: {e}")
        return False
