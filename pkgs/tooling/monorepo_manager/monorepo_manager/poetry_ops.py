#!/usr/bin/env python3
"""
poetry_ops.py

Provides functions to:
  - Install Poetry
  - Run 'poetry lock' and 'poetry install'
  - Extract path dependencies from pyproject.toml
  - Recursively build packages (based on the dependencies)
  - Show the installed packages (via pip freeze)
  - Set versions and dependency versions in pyproject.toml files
  - Publish built packages to PyPI
  - Publish packages based on path dependencies

Intended for use in a unified monorepo management CLI.
"""

import argparse
import os
import subprocess
import sys
import toml


def run_command(command, cwd=None):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            shell=True,
            check=True,
        )
        if result.stdout:
            print(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr}", file=sys.stderr)
        sys.exit(e.returncode)


def install_poetry():
    """Install Poetry."""
    print("Installing Poetry...")
    run_command("curl -sSL https://install.python-poetry.org | python3")
    # Update PATH so that ~/.local/bin is included for subsequent commands.
    os.environ["PATH"] = f"{os.path.expanduser('~')}/.local/bin:{os.environ.get('PATH', '')}"


def poetry_lock(directory=None, file=None):
    """
    Run 'poetry lock' in the specified directory or on the specified file's directory.
    
    :param directory: Directory containing pyproject.toml.
    :param file: Path to a specific pyproject.toml file.
    """
    location = directory if directory else os.path.dirname(file)
    print(f"Generating poetry.lock in {location}...")
    run_command("poetry lock", cwd=location)


def poetry_install(directory=None, file=None, extras=None, with_dev=False, all_extras=False):
    """
    Run 'poetry install' in the specified directory or file.
    
    :param directory: Directory containing pyproject.toml.
    :param file: Path to a specific pyproject.toml file.
    :param extras: Extras to include (e.g., "full").
    :param with_dev: Boolean flag to include dev dependencies.
    :param all_extras: Boolean flag to include all extras.
    """
    location = directory if directory else os.path.dirname(file)
    print(f"Installing dependencies in {location}...")
    command = ["poetry", "install", "--no-cache", "-vv"]
    if all_extras:
        command.append("--all-extras")
    elif extras:
        command.append(f"--extras {extras}")
    if with_dev:
        command.append("--with dev")
    run_command(" ".join(command), cwd=location)


def extract_path_dependencies(pyproject_path):
    """
    Extract path dependencies from a pyproject.toml file.
    
    Looks for dependency entries that are defined as tables with a "path" key.
    
    :param pyproject_path: Path to the pyproject.toml file.
    :return: List of dependency paths found.
    """
    print(f"Extracting path dependencies from {pyproject_path}...")
    try:
        with open(pyproject_path, "r") as f:
            data = toml.load(f)
    except Exception as e:
        print(f"Error reading {pyproject_path}: {e}", file=sys.stderr)
        sys.exit(1)

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    path_deps = [v["path"] for v in dependencies.values() if isinstance(v, dict) and "path" in v]
    return path_deps


def recursive_build(directory=None, file=None):
    """
    Recursively build packages based on path dependencies extracted from a pyproject.toml.
    
    :param directory: Directory containing pyproject.toml.
    :param file: Specific pyproject.toml file to use.
    """
    pyproject_path = file if file else os.path.join(directory, "pyproject.toml")
    base_dir = os.path.dirname(pyproject_path)
    dependencies = extract_path_dependencies(pyproject_path)

    print("Building specified packages...")
    for package_path in dependencies:
        full_path = os.path.join(base_dir, package_path)
        pyproject_file = os.path.join(full_path, "pyproject.toml")
        if os.path.isdir(full_path) and os.path.isfile(pyproject_file):
            print(f"Building package: {full_path}")
            run_command("poetry build", cwd=full_path)
        else:
            print(f"Skipping {full_path}: not a valid package directory")


def show_pip_freeze():
    """
    Show the installed packages using pip freeze.
    """
    print("Installed packages (pip freeze):")
    run_command("pip freeze")


def set_version_in_pyproject(version, directory=None, file=None):
    """
    Set the version for the package in the pyproject.toml file(s).
    
    :param version: The new version string to set.
    :param directory: If provided, recursively update all pyproject.toml files found in the directory.
    :param file: If provided, update the specific pyproject.toml file.
    """
    def update_file(pyproject_file, version):
        print(f"Setting version to {version} in {pyproject_file}...")
        try:
            with open(pyproject_file, "r") as f:
                data = toml.load(f)
        except Exception as e:
            print(f"Error reading {pyproject_file}: {e}", file=sys.stderr)
            return

        if "tool" in data and "poetry" in data["tool"]:
            data["tool"]["poetry"]["version"] = version
        else:
            print(f"Invalid pyproject.toml structure in {pyproject_file}.", file=sys.stderr)
            return

        try:
            with open(pyproject_file, "w") as f:
                toml.dump(data, f)
            print(f"Version set to {version} in {pyproject_file}.")
        except Exception as e:
            print(f"Error writing {pyproject_file}: {e}", file=sys.stderr)

    if directory:
        for root, _, files in os.walk(directory):
            if "pyproject.toml" in files:
                pyproject_file = os.path.join(root, "pyproject.toml")
                update_file(pyproject_file, version)
    elif file:
        update_file(file, version)
    else:
        print("Error: A directory or a file must be specified.", file=sys.stderr)
        sys.exit(1)


def set_dependency_versions(version, directory=None, file=None):
    """
    Update versions for path dependencies found in pyproject.toml files.
    
    For each dependency that is defined with a "path", update its version to '^<version>'.
    Also attempts to update the dependency's own pyproject.toml.
    
    :param version: The new version string (without the caret).
    :param directory: A directory to search for pyproject.toml files.
    :param file: A specific pyproject.toml file to update.
    """
    def update_file(pyproject_file, version):
        print(f"Setting dependency versions to {version} in {pyproject_file}...")
        try:
            with open(pyproject_file, "r") as f:
                data = toml.load(f)
        except Exception as e:
            print(f"Error reading {pyproject_file}: {e}", file=sys.stderr)
            return

        dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        updated_dependencies = {}

        for dep_name, dep_value in dependencies.items():
            if isinstance(dep_value, dict) and "path" in dep_value:
                # Update the version entry while preserving other keys except 'path'
                updated_dep = {"version": f"^{version}"}
                for key, val in dep_value.items():
                    if key != "path":
                        updated_dep[key] = val
                updated_dependencies[dep_name] = updated_dep

                # Update the dependency's own pyproject.toml file if present.
                dependency_path = os.path.join(os.path.dirname(pyproject_file), dep_value["path"])
                dependency_pyproject = os.path.join(dependency_path, "pyproject.toml")
                if os.path.isfile(dependency_pyproject):
                    print(f"Updating version in dependency: {dependency_pyproject} to {version}")
                    set_version_in_pyproject(version, file=dependency_pyproject)
                else:
                    print(f"Warning: pyproject.toml not found at {dependency_pyproject}")
            else:
                updated_dependencies[dep_name] = dep_value

        # Write back the updated dependencies.
        if "tool" in data and "poetry" in data["tool"]:
            data["tool"]["poetry"]["dependencies"] = updated_dependencies
        else:
            print(f"Error: Invalid pyproject.toml structure in {pyproject_file}.", file=sys.stderr)
            return

        try:
            with open(pyproject_file, "w") as f:
                toml.dump(data, f)
            print(f"Dependency versions set to {version} in {pyproject_file}.")
        except Exception as e:
            print(f"Error writing {pyproject_file}: {e}", file=sys.stderr)

    if directory:
        for root, _, files in os.walk(directory):
            if "pyproject.toml" in files:
                update_file(os.path.join(root, "pyproject.toml"), version)
    elif file:
        update_file(file, version)
    else:
        print("Error: A directory or a file must be specified.", file=sys.stderr)
        sys.exit(1)


def publish_package(directory=None, file=None, username=None, password=None):
    """
    Build and publish packages to PyPI.
    
    :param directory: Directory containing one or more packages.
    :param file: Specific pyproject.toml file to use.
    :param username: PyPI username.
    :param password: PyPI password.
    """
    if directory:
        print(f"Publishing all packages in {directory} and its subdirectories...")
        for root, dirs, files in os.walk(directory):
            if "pyproject.toml" in files:
                print(f"Publishing package from {root}...")
                run_command("poetry build", cwd=root)
                run_command(
                    f"poetry publish --username {username} --password {password}",
                    cwd=root,
                )
    elif file:
        location = os.path.dirname(file)
        print(f"Publishing package from {location}...")
        run_command("poetry build", cwd=location)
        run_command(
            f"poetry publish --username {username} --password {password}",
            cwd=location,
        )
    else:
        print("Error: Either a directory or a file must be specified.", file=sys.stderr)
        sys.exit(1)


def publish_from_dependencies(directory=None, file=None, username=None, password=None):
    """
    Build and publish packages based on path dependencies defined in a pyproject.toml.
    
    :param directory: Directory containing the base pyproject.toml.
    :param file: Specific pyproject.toml file.
    :param username: PyPI username.
    :param password: PyPI password.
    """
    pyproject_path = file if file else os.path.join(directory, "pyproject.toml")
    if not os.path.isfile(pyproject_path):
        print(f"pyproject.toml not found at {pyproject_path}", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(pyproject_path)
    dependencies = extract_path_dependencies(pyproject_path)
    print("Building and publishing packages based on path dependencies...")
    for package_path in dependencies:
        full_path = os.path.join(base_dir, package_path)
        pyproject_file = os.path.join(full_path, "pyproject.toml")
        if os.path.isdir(full_path) and os.path.isfile(pyproject_file):
            print(f"Building and publishing package: {full_path}")
            run_command("poetry build", cwd=full_path)
            run_command(
                f"poetry publish --username {username} --password {password}",
                cwd=full_path,
            )
        else:
            print(f"Skipping {full_path}: not a valid package directory")
