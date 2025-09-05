#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import toml


def run_command(command, cwd=None):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(
            command, cwd=cwd, text=True, capture_output=True, shell=True, check=True
        )
        print(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr}", file=sys.stderr)
        sys.exit(e.returncode)


def install_poetry():
    """Install Poetry."""
    print("Installing Poetry...")
    run_command("curl -sSL https://install.python-poetry.org | python3")
    os.environ["PATH"] = f"{os.path.expanduser('~')}/.local/bin:{os.environ['PATH']}"


def poetry_lock(directory=None, file=None):
    """Run `poetry lock` in the specified directory or file."""
    location = directory if directory else os.path.dirname(file)
    print(f"Generating poetry.lock in {location}...")
    command = ["poetry", "lock"]
    run_command(" ".join(command), cwd=location)


def poetry_install(
    directory=None, file=None, extras=None, with_dev=False, all_extras=False
):
    """Run `poetry install` in the specified directory or file."""
    location = directory if directory else os.path.dirname(file)
    print(f"Installing dependencies in {location}...")
    command = ["poetry", "install", "--no-cache", "-vv"]
    if all_extras:
        command.append("--all-extras")
    elif extras:
        command += [f"--extras {extras}"]
    if with_dev:
        command.append("--with dev")
    run_command(" ".join(command), cwd=location)


def extract_path_dependencies(pyproject_path):
    """Extract path dependencies from a pyproject.toml file."""
    print(f"Extracting path dependencies from {pyproject_path}...")
    with open(pyproject_path, "r") as f:
        data = toml.load(f)

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    path_deps = [
        v["path"] for v in dependencies.values() if isinstance(v, dict) and "path" in v
    ]
    return path_deps


def recursive_build(directory=None, file=None):
    """Recursively build packages based on dependencies."""
    pyproject_path = file if file else os.path.join(directory, "pyproject.toml")
    base_dir = os.path.dirname(pyproject_path)
    dependencies = extract_path_dependencies(pyproject_path)

    print("Building specified packages...")
    for package_path in dependencies:
        full_path = os.path.join(base_dir, package_path)
        if os.path.isdir(full_path) and os.path.isfile(
            os.path.join(full_path, "pyproject.toml")
        ):
            print(f"Building package: {full_path}")
            run_command("poetry build", cwd=full_path)
        else:
            print(f"Skipping {full_path}: not a valid package directory")


def show_pip_freeze():
    """Show the installed packages using pip freeze."""
    print("Installed packages (pip freeze):")
    run_command("pip freeze")


def set_version(version, directory=None, file=None):
    """
    Set the version in the pyproject.toml file or all files within a directory.
    """
    if directory:
        for root, _, files in os.walk(directory):
            if "pyproject.toml" in files:
                pyproject_path = os.path.join(root, "pyproject.toml")
                print(f"Setting version to {version} in {pyproject_path}...")

                with open(pyproject_path, "r") as f:
                    data = toml.load(f)

                # Update the version field if it's a valid structure
                if "tool" in data and "poetry" in data["tool"]:
                    data["tool"]["poetry"]["version"] = version
                else:
                    print(
                        f"Error: Invalid pyproject.toml structure in {pyproject_path}.",
                        file=sys.stderr,
                    )
                    continue

                # Write the updated content back to the file
                with open(pyproject_path, "w") as f:
                    toml.dump(data, f)

                print(f"Version set to {version} in {pyproject_path}.")
    elif file:
        pyproject_path = file
        print(f"Setting version to {version} in {pyproject_path}...")

        with open(pyproject_path, "r") as f:
            data = toml.load(f)

        # Update the version field if it's a valid structure
        if "tool" in data and "poetry" in data["tool"]:
            data["tool"]["poetry"]["version"] = version
        else:
            print(
                f"Error: Invalid pyproject.toml structure in {pyproject_path}.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Write the updated content back to the file
        with open(pyproject_path, "w") as f:
            toml.dump(data, f)

        print(f"Version set to {version} in {pyproject_path}.")


def set_dependency_versions(version, directory=None, file=None):
    """
    Update path dependencies in all pyproject.toml files within a directory or a specific file.
    """
    if directory:
        for root, _, files in os.walk(directory):
            if "pyproject.toml" in files:
                pyproject_path = os.path.join(root, "pyproject.toml")
                print(
                    f"Setting dependency versions to {version} in {pyproject_path}..."
                )

                with open(pyproject_path, "r") as f:
                    data = toml.load(f)

                dependencies = (
                    data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                )
                updated_dependencies = {}

                for dep_name, dep_value in dependencies.items():
                    if isinstance(dep_value, dict) and "path" in dep_value:
                        # Maintain the `path` and only update the `version` key
                        updated_dep = {"version": f"^{version}"}
                        for key in dep_value:
                            if key != "path":  # Preserve the `path` key
                                updated_dep[key] = dep_value[key]
                        updated_dependencies[dep_name] = updated_dep

                        # Update the version in the dependency's pyproject.toml
                        dependency_path = os.path.join(root, dep_value["path"])
                        dependency_pyproject = os.path.join(
                            dependency_path, "pyproject.toml"
                        )
                        if os.path.isfile(dependency_pyproject):
                            print(
                                f"Updating version in {dependency_pyproject} to {version}..."
                            )
                            set_version(version=version, file=dependency_pyproject)
                        else:
                            print(
                                f"Warning: pyproject.toml not found at {dependency_pyproject}"
                            )

                    else:
                        # Leave other dependencies unchanged
                        updated_dependencies[dep_name] = dep_value

                # Write back to the `dependencies` section
                data["tool"]["poetry"]["dependencies"] = updated_dependencies

                # Serialize and write the updated toml back to the file
                with open(pyproject_path, "w") as f:
                    toml.dump(data, f)

                print(f"Dependency versions set to {version} in {pyproject_path}.")
    elif file:
        pyproject_path = file
        print(f"Setting dependency versions to {version} in {pyproject_path}...")

        with open(pyproject_path, "r") as f:
            data = toml.load(f)

        dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        updated_dependencies = {}

        for dep_name, dep_value in dependencies.items():
            if isinstance(dep_value, dict) and "path" in dep_value:
                # Maintain the `path` and only update the `version` key
                updated_dep = {"version": f"^{version}"}
                for key in dep_value:
                    if key != "path":  # Preserve the `path` key
                        updated_dep[key] = dep_value[key]
                updated_dependencies[dep_name] = updated_dep

                # Update the version in the dependency's pyproject.toml
                dependency_path = os.path.join(
                    os.path.dirname(pyproject_path), dep_value["path"]
                )
                dependency_pyproject = os.path.join(dependency_path, "pyproject.toml")
                if os.path.isfile(dependency_pyproject):
                    print(f"Updating version in {dependency_pyproject} to {version}...")
                    set_version(version=version, file=dependency_pyproject)
                else:
                    print(
                        f"Warning: pyproject.toml not found at {dependency_pyproject}"
                    )

            else:
                # Leave other dependencies unchanged
                updated_dependencies[dep_name] = dep_value

        # Write back to the `dependencies` section
        data["tool"]["poetry"]["dependencies"] = updated_dependencies

        # Serialize and write the updated toml back to the file
        with open(pyproject_path, "w") as f:
            toml.dump(data, f)

        print(f"Dependency versions set to {version} in {pyproject_path}.")


def publish_package(directory=None, file=None, username=None, password=None):
    """Build and publish packages to PyPI from a directory or specific file."""
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
    """Build and publish packages based on path dependencies from a pyproject.toml file."""
    pyproject_path = file if file else os.path.join(directory, "pyproject.toml")
    if not os.path.isfile(pyproject_path):
        print(f"pyproject.toml not found at {pyproject_path}", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(pyproject_path)
    dependencies = extract_path_dependencies(pyproject_path)

    print("Building and publishing packages based on path dependencies...")
    for package_path in dependencies:
        full_path = os.path.join(base_dir, package_path)
        if os.path.isdir(full_path) and os.path.isfile(
            os.path.join(full_path, "pyproject.toml")
        ):
            print(f"Building and publishing package: {full_path}")
            run_command("poetry build", cwd=full_path)
            run_command(
                f"poetry publish --username {username} --password {password}",
                cwd=full_path,
            )
        else:
            print(f"Skipping {full_path}: not a valid package directory")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Python packages in a monorepo."
    )
    subparsers = parser.add_subparsers(
        dest="action", required=True, help="Action to perform."
    )

    # Shared arguments for directory and file
    location_parser = argparse.ArgumentParser(add_help=False)
    location_parser.add_argument(
        "--directory", type=str, help="Path to the directory containing pyproject.toml."
    )
    location_parser.add_argument(
        "--file", type=str, help="Path to the pyproject.toml file."
    )

    # Poetry lock
    subparsers.add_parser(
        "poetry-lock", parents=[location_parser], help="Run `poetry lock`."
    )

    # Poetry install
    install_parser = subparsers.add_parser(
        "poetry-install", parents=[location_parser], help="Run `poetry install`."
    )
    install_parser.add_argument(
        "--extras", type=str, help="Extras to include (e.g., full, dev)."
    )
    install_parser.add_argument(
        "--dev", action="store_true", help="Include dev dependencies."
    )
    install_parser.add_argument(
        "--all-extras", action="store_true", help="Include all extras."
    )

    # Extract path dependencies
    subparsers.add_parser(
        "extract-path-dependencies",
        parents=[location_parser],
        help="Extract path dependencies from pyproject.toml.",
    )

    # Recursive build
    subparsers.add_parser(
        "recursive-build",
        parents=[location_parser],
        help="Recursively build packages based on path dependencies.",
    )

    # Show pip freeze
    subparsers.add_parser(
        "show-pip-freeze", help="Show installed packages using pip freeze."
    )

    # Set dependency versions
    version_parser = subparsers.add_parser(
        "set-dependency-versions",
        parents=[location_parser],
        help="Set dependency versions and update paths.",
    )
    version_parser.add_argument(
        "--version", type=str, required=True, help="The new version."
    )

    # Set version
    set_version_parser = subparsers.add_parser(
        "set-version",
        parents=[location_parser],
        help="Set the version in pyproject.toml.",
    )
    set_version_parser.add_argument(
        "--version", type=str, required=True, help="The new version."
    )

    # Publish
    publish_parser = subparsers.add_parser(
        "publish", parents=[location_parser], help="Publish package to PyPI."
    )
    publish_parser.add_argument(
        "--username", type=str, required=True, help="PyPI username."
    )
    publish_parser.add_argument(
        "--password", type=str, required=True, help="PyPI password."
    )

    # Publish from dependencies
    publish_deps_parser = subparsers.add_parser(
        "publish-from-dependencies",
        parents=[location_parser],
        help="Build and publish packages based on path dependencies from pyproject.toml.",
    )
    publish_deps_parser.add_argument(
        "--username", type=str, required=True, help="PyPI username."
    )
    publish_deps_parser.add_argument(
        "--password", type=str, required=True, help="PyPI password."
    )

    args = parser.parse_args()

    # Action dispatch
    if args.action == "poetry-lock":
        poetry_lock(directory=args.directory, file=args.file)

    elif args.action == "poetry-install":
        poetry_install(
            directory=args.directory,
            file=args.file,
            extras=args.extras,
            with_dev=args.dev,
            all_extras=args.all_extras,
        )

    elif args.action == "extract-path-dependencies":
        pyproject_path = (
            args.file if args.file else os.path.join(args.directory, "pyproject.toml")
        )
        dependencies = extract_path_dependencies(pyproject_path)
        print(",".join(dependencies))

    elif args.action == "recursive-build":
        recursive_build(directory=args.directory, file=args.file)

    elif args.action == "show-pip-freeze":
        show_pip_freeze()

    elif args.action == "set-dependency-versions":
        set_dependency_versions(
            version=args.version, directory=args.directory, file=args.file
        )

    elif args.action == "set-version":
        set_version(version=args.version, directory=args.directory, file=args.file)

    elif args.action == "publish":
        publish_package(
            directory=args.directory,
            file=args.file,
            username=args.username,
            password=args.password,
        )

    elif args.action == "publish-from-dependencies":
        publish_from_dependencies(
            directory=args.directory,
            file=args.file,
            username=args.username,
            password=args.password,
        )


if __name__ == "__main__":
    main()
