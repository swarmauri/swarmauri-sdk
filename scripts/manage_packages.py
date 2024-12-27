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


def poetry_lock(directory=None, file=None, extras=None, with_dev=False):
    """Run `poetry lock` in the specified directory or file."""
    location = directory if directory else os.path.dirname(file)
    print(f"Generating poetry.lock in {location}...")
    command = ["poetry", "lock"]
    if extras:
        command += [f"--with {extras}"]
    if with_dev:
        command.append("--with dev")
    run_command(" ".join(command), cwd=location)


def poetry_install(directory=None, file=None, extras=None, with_dev=False):
    """Run `poetry install` in the specified directory or file."""
    location = directory if directory else os.path.dirname(file)
    print(f"Installing dependencies in {location}...")
    command = ["poetry", "install", "--no-cache", "-vv"]
    if extras:
        command += [f"--with {extras}"]
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
        if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "pyproject.toml")):
            print(f"Building package: {full_path}")
            run_command("poetry build", cwd=full_path)
        else:
            print(f"Skipping {full_path}: not a valid package directory")


def show_pip_freeze():
    """Show the installed packages using pip freeze."""
    print("Installed packages (pip freeze):")
    run_command("pip freeze")


def main():
    parser = argparse.ArgumentParser(description="Manage Python packages in a monorepo.")
    subparsers = parser.add_subparsers(dest="action", required=True, help="Action to perform.")

    # Shared arguments for directory and file
    location_parser = argparse.ArgumentParser(add_help=False)
    location_parser.add_argument("--directory", type=str, help="Path to the directory containing pyproject.toml.")
    location_parser.add_argument("--file", type=str, help="Path to the pyproject.toml file.")

    # Poetry lock
    lock_parser = subparsers.add_parser("poetry-lock", parents=[location_parser], help="Run `poetry lock`.")
    lock_parser.add_argument("--extras", type=str, help="Extras to include (e.g., full, dev).")
    lock_parser.add_argument("--dev", action="store_true", help="Include dev dependencies.")

    # Poetry install
    install_parser = subparsers.add_parser("poetry-install", parents=[location_parser], help="Run `poetry install`.")
    install_parser.add_argument("--extras", type=str, help="Extras to include (e.g., full, dev).")
    install_parser.add_argument("--dev", action="store_true", help="Include dev dependencies.")

    # Extract path dependencies
    subparsers.add_parser(
        "extract-path-dependencies", parents=[location_parser], help="Extract path dependencies from pyproject.toml."
    )

    # Recursive build
    subparsers.add_parser(
        "recursive-build", parents=[location_parser], help="Recursively build packages based on path dependencies."
    )

    # Show pip freeze
    subparsers.add_parser("show-pip-freeze", help="Show installed packages using pip freeze.")

    args = parser.parse_args()

    # Action dispatch
    if args.action == "poetry-lock":
        poetry_lock(directory=args.directory, file=args.file, extras=args.extras, with_dev=args.dev)

    elif args.action == "poetry-install":
        poetry_install(directory=args.directory, file=args.file, extras=args.extras, with_dev=args.dev)

    elif args.action == "extract-path-dependencies":
        pyproject_path = args.file if args.file else os.path.join(args.directory, "pyproject.toml")
        dependencies = extract_path_dependencies(pyproject_path)
        print(",".join(dependencies))

    elif args.action == "recursive-build":
        recursive_build(directory=args.directory, file=args.file)

    elif args.action == "show-pip-freeze":
        show_pip_freeze()


if __name__ == "__main__":
    main()
