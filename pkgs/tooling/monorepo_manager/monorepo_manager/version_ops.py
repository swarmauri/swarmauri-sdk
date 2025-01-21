#!/usr/bin/env python3
"""
version_ops.py

Provides functions to:
  - Read the current version from pyproject.toml.
  - Bump the current version (major, minor, patch) or finalize a dev release.
  - Validate that a user-provided new version is not lower than the current one.
  - Update the pyproject.toml with the new version.

Intended for use in a unified monorepo management CLI.
"""

import sys
from packaging.version import Version, InvalidVersion
from tomlkit import parse, dumps


def read_pyproject_version(file_path):
    """
    Reads the current version from the provided pyproject.toml file.

    Args:
        file_path (str): Path to the pyproject.toml file.

    Returns:
        tuple: A tuple containing the current version string and the
               tomlkit Document representing the file.
    Raises:
        KeyError: If the version key is missing.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    doc = parse(content)
    try:
        version = doc["tool"]["poetry"]["version"]
    except KeyError:
        raise KeyError("No version found under [tool.poetry] in the given pyproject.toml")
    return version, doc


def bump_version(current_version, bump_type):
    """
    Bumps the current version up using semantic versioning.
    Supports:
      - Bumping stable versions (major, minor, patch) which also start a dev cycle.
      - Bumping within a dev cycle.
      - Finalizing a dev version (removing the .dev suffix).

    Args:
        current_version (str): The current version (e.g. "1.0.0" or "1.0.1.dev2").
        bump_type (str): One of "major", "minor", "patch", or "finalize".

    Returns:
        str: The new version string.
    Raises:
        ValueError: If the current version is invalid or the bump operation cannot be performed.
    """
    try:
        ver = Version(current_version)
    except InvalidVersion as e:
        raise ValueError(f"Invalid current version '{current_version}': {e}")

    # Check if it's a dev release
    is_dev = ver.dev is not None
    major, minor, patch = ver.release

    if bump_type == "finalize":
        if is_dev:
            # Remove the dev segment
            new_version = f"{major}.{minor}.{patch}"
        else:
            raise ValueError("Current version is stable; nothing to finalize.")
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
        new_version = f"{major}.{minor}.{patch}.dev1"
    elif bump_type == "minor":
        minor += 1
        patch = 0
        new_version = f"{major}.{minor}.{patch}.dev1"
    elif bump_type == "patch":
        if is_dev:
            # Increment the dev counter if already in a dev cycle.
            new_dev = ver.dev + 1
            new_version = f"{major}.{minor}.{patch}.dev{new_dev}"
        else:
            patch += 1
            new_version = f"{major}.{minor}.{patch}.dev1"
    else:
        raise ValueError("bump_type must be one of: 'major', 'minor', 'patch', or 'finalize'")

    return new_version


def validate_and_set_version(current_version, new_version):
    """
    Validates that the new version is not lower than the current version.

    Args:
        current_version (str): The current version string.
        new_version (str): The target version string.

    Returns:
        str: The new version if it is valid.
    Raises:
        ValueError: If new_version is lower than current_version.
    """
    try:
        cur_ver = Version(current_version)
        tgt_ver = Version(new_version)
    except InvalidVersion as e:
        raise ValueError(f"Invalid version provided: {e}")

    if tgt_ver < cur_ver:
        raise ValueError("You cannot bump the version downwards. The target version must be higher than the current version.")
    
    return new_version


def update_pyproject_version(file_path, new_version):
    """
    Updates the pyproject.toml file with the new version.

    Args:
        file_path (str): The path to the pyproject.toml file.
        new_version (str): The new version string.
    
    Returns:
        None
    """
    try:
        current_version, doc = read_pyproject_version(file_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Update the version field if it exists
    if "tool" in doc and "poetry" in doc["tool"]:
        doc["tool"]["poetry"]["version"] = new_version
    else:
        print(f"Error: Invalid pyproject.toml structure in {file_path}.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "w") as f:
            f.write(dumps(doc))
    except Exception as e:
        print(f"Error writing updated pyproject.toml: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Bumped version from {current_version} to {new_version} in {file_path}.")


def bump_or_set_version(pyproject_file, bump=None, set_ver=None):
    """
    Executes either a version bump or a direct version set on the given pyproject.toml file.
    
    Args:
        pyproject_file (str): Path to the pyproject.toml file.
        bump (str, optional): The type of bump ("major", "minor", "patch", or "finalize").
        set_ver (str, optional): A specific version string to set.
    
    Returns:
        None
    """
    try:
        current_version, _ = read_pyproject_version(pyproject_file)
    except Exception as e:
        print(f"Error reading current version: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if bump:
            new_version = bump_version(current_version, bump)
        elif set_ver:
            new_version = validate_and_set_version(current_version, set_ver)
        else:
            print("No version operation specified.", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    update_pyproject_version(pyproject_file, new_version)


# Example usage when running this module directly.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Bump or set version in pyproject.toml using semantic versioning."
    )
    parser.add_argument("file", help="Path to the pyproject.toml file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bump", choices=["major", "minor", "patch", "finalize"], help="Type of version bump to perform")
    group.add_argument("--set", dest="set_ver", help="Set the version explicitly (e.g. 1.2.3 or 1.2.3.dev1)")
    
    args = parser.parse_args()
    bump_or_set_version(args.file, bump=args.bump, set_ver=args.set_ver)
