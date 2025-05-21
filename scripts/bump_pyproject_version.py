# /// script
# dependencies = [
#   "tomlkit>=0.13.2",
#   "packaging>=24.2",
# ]
# ///

"""bump_pyproject_version.py

Bump or set a version in ``pyproject.toml``.

Call this script with the file path and either ``--bump`` or ``--set`` to
increment or assign the version using semantic versioning rules.
"""

import sys
import argparse
from packaging.version import Version, InvalidVersion
from tomlkit import parse, dumps


def read_pyproject_version(file_path):
    """
    Reads the current version from the provided pyproject.toml file.

    Args:
        file_path (str): Path to the pyproject.toml file.

    Returns:
        (str, Document): A tuple containing the current version string and the
                         tomlkit Document.
    """
    with open(file_path, "r") as f:
        content = f.read()
    doc = parse(content)
    try:
        version = doc["project"]["version"]
    except KeyError:
        raise KeyError(
            'No version found under ["project"][version] in the given pyproject.toml'
        )
    return version, doc


def bump_version(current_version, bump_type):
    """
    Bumps the current version up using semantic versioning.
    This function supports:
      - Bumping a stable version to start a dev cycle.
      - Bumping within a dev cycle.
      - Finalizing a dev version (i.e. removing the .dev suffix).

    Args:
        current_version (str): The current version (e.g. "1.0.0" or "1.0.1.dev2").
        bump_type (str): Type of bump: "major", "minor", "patch", or "finalize".

    Returns:
        str: The new version string.
    """
    try:
        ver = Version(current_version)
    except InvalidVersion as e:
        raise ValueError(f"Invalid current version '{current_version}': {e}")

    # Is this a dev version?
    is_dev = ver.dev is not None
    major, minor, patch = ver.release

    if bump_type == "finalize":
        if is_dev:
            # Remove the dev segment to finalize this dev release.
            new_version = f"{major}.{minor}.{patch}"
        else:
            raise ValueError("Current version is stable; nothing to finalize.")
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
        new_version = f"{major}.{minor}.{patch}"
        # Always start a dev cycle for a bump if desired.
        new_version += ".dev1"
    elif bump_type == "minor":
        minor += 1
        patch = 0
        new_version = f"{major}.{minor}.{patch}"
        new_version += ".dev1"
    elif bump_type == "patch":
        if is_dev:
            # If already in a dev cycle, bump the dev counter.
            new_dev = ver.dev + 1
            new_version = f"{major}.{minor}.{patch}.dev{new_dev}"
        else:
            # For a stable version, bump the patch and start a dev cycle.
            patch += 1
            new_version = f"{major}.{minor}.{patch}.dev1"
    else:
        raise ValueError(
            "bump_type must be one of: 'major', 'minor', 'patch', or 'finalize'"
        )

    return new_version


def set_version(current_version, new_version):
    """
    Validates that the new version is not lower than the current version.

    Args:
        current_version (str): The current version.
        new_version (str): The version to be set.

    Returns:
        str: The new version if it's valid.

    Raises:
        ValueError: If new_version is lower than current_version.
    """
    try:
        current_ver = Version(current_version)
        new_ver = Version(new_version)
    except InvalidVersion as e:
        raise ValueError(f"Invalid version provided: {e}")

    if new_ver < current_ver:
        raise ValueError(
            "You cannot bump the version downwards. The target version must be higher than the current version."
        )

    return new_version


def update_pyproject_version(file_path, new_version):
    """
    Updates the pyproject.toml file with the specified new version.

    Args:
        file_path (str): The path to the pyproject.toml file.
        new_version (str): The new version string to set.

    Returns:
        None
    """
    current_version, doc = read_pyproject_version(file_path)
    doc["project"]["version"] = new_version
    with open(file_path, "w") as f:
        f.write(dumps(doc))
    print(f"Bumped version from {current_version} to {new_version} in {file_path}.")


def main():
    parser = argparse.ArgumentParser(
        description="Bump or set version in pyproject.toml using semantic versioning. Supports .dev versions and finalizing dev releases."
    )
    parser.add_argument("file", help="Path to the pyproject.toml file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--bump",
        choices=["major", "minor", "patch", "finalize"],
        help="Type of version bump (use 'finalize' to remove the .dev segment from a dev release)",
    )
    group.add_argument(
        "--set",
        dest="set_version",
        help="Set the version explicitly (e.g. 0.2.0 or 0.2.0.dev1)",
    )

    args = parser.parse_args()

    current_version, _ = read_pyproject_version(args.file)

    try:
        if args.bump:
            new_version = bump_version(current_version, args.bump)
        elif args.set_version:
            new_version = set_version(current_version, args.set_version)
        else:
            print("No operation specified.")
            sys.exit(1)

        update_pyproject_version(args.file, new_version)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
