#!/usr/bin/env python3
"""
cli.py

This is the main entry point for the monorepo management CLI.
It provides commands to:
  - Manage Poetry-based operations (lock, install, build, show pip-freeze, publish)
  - Manage version operations (bump or set versions in pyproject.toml)
  - Manage remote operations (fetch/update Git dependency versions)
  - Run tests using pytest (with optional parallelism)
  - Analyze test results from a JSON file
  - Operate on pyproject.toml files (extract and update dependency versions)

The commands are intentionally named with simple terms (e.g. "lock" instead of "poetry lock",
"install" instead of "poetry install", and "test" instead of "test-analyze").
"""

import argparse
import sys

# Import operations from the local modules.
from monorepo_manager import poetry_ops
from monorepo_manager import version_ops
from monorepo_manager import remote_ops
from monorepo_manager import test_ops
from monorepo_manager import pyproject_ops


def main():
    parser = argparse.ArgumentParser(
        description="A CLI for managing a Python monorepo with multiple standalone packages."
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # ------------------------------------------------
    # Command: lock
    # ------------------------------------------------
    lock_parser = subparsers.add_parser("lock", help="Generate a poetry.lock file")
    lock_parser.add_argument(
        "--directory", type=str, help="Directory containing a pyproject.toml"
    )
    lock_parser.add_argument(
        "--file", type=str, help="Explicit path to a pyproject.toml file"
    )

    # ------------------------------------------------
    # Command: install
    # ------------------------------------------------
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument(
        "--directory", type=str, help="Directory containing a pyproject.toml"
    )
    install_parser.add_argument(
        "--file", type=str, help="Explicit path to a pyproject.toml file"
    )
    install_parser.add_argument(
        "--extras", type=str, help="Extras to include (e.g. 'full')"
    )
    install_parser.add_argument(
        "--dev", action="store_true", help="Include dev dependencies"
    )
    install_parser.add_argument(
        "--all-extras", action="store_true", help="Include all extras"
    )

    # ------------------------------------------------
    # Command: build
    # ------------------------------------------------
    build_parser = subparsers.add_parser(
        "build", help="Build packages recursively based on path dependencies"
    )
    build_parser.add_argument(
        "--directory", type=str, help="Directory containing pyproject.toml"
    )
    build_parser.add_argument(
        "--file", type=str, help="Explicit path to a pyproject.toml file"
    )

    # ------------------------------------------------
    # Command: version
    # ------------------------------------------------
    version_parser = subparsers.add_parser(
        "version", help="Bump or set package version"
    )
    version_parser.add_argument(
        "pyproject_file", type=str, help="Path to the pyproject.toml file"
    )
    vgroup = version_parser.add_mutually_exclusive_group(required=True)
    vgroup.add_argument(
        "--bump",
        choices=["major", "minor", "patch", "finalize"],
        help="Bump the version (e.g. patch, major, minor, finalize)",
    )
    vgroup.add_argument(
        "--set", dest="set_ver", help="Explicit version to set (e.g. 2.0.0.dev1)"
    )

    # ------------------------------------------------
    # Command: remote
    # ------------------------------------------------
    remote_parser = subparsers.add_parser(
        "remote", help="Remote operations for Git dependencies"
    )
    remote_subparsers = remote_parser.add_subparsers(dest="remote_cmd", required=True)

    # remote fetch: fetch version from remote GitHub pyproject.toml
    fetch_parser = remote_subparsers.add_parser(
        "fetch", help="Fetch version from remote GitHub pyproject.toml"
    )
    fetch_parser.add_argument(
        "--git-url", type=str, required=True, help="GitHub repository URL"
    )
    fetch_parser.add_argument(
        "--branch", type=str, default="main", help="Branch name (default: main)"
    )
    fetch_parser.add_argument(
        "--subdir",
        type=str,
        default="",
        help="Subdirectory where pyproject.toml is located",
    )

    # remote update: update a local pyproject.toml with remote resolved versions.
    update_parser = remote_subparsers.add_parser(
        "update", help="Update local pyproject.toml with remote versions"
    )
    update_parser.add_argument(
        "--input", required=True, help="Path to the local pyproject.toml"
    )
    update_parser.add_argument(
        "--output", help="Optional output file path (defaults to overwriting the input)"
    )

    # ------------------------------------------------
    # Command: test (run pytest)
    # ------------------------------------------------
    test_parser = subparsers.add_parser("test", help="Run tests using pytest")
    test_parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory to run tests in (default: current directory)",
    )
    test_parser.add_argument(
        "--num-workers",
        type=int,
        default=1,
        help="Number of workers for parallel testing (requires pytest-xdist)",
    )

    # ------------------------------------------------
    # Command: analyze (analyze test results from JSON)
    # ------------------------------------------------
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze test results from a JSON file"
    )
    analyze_parser.add_argument("file", help="Path to the JSON file with test results")
    analyze_parser.add_argument(
        "--required-passed", type=str, help="Threshold for passed tests (e.g. 'gt:75')"
    )
    analyze_parser.add_argument(
        "--required-skipped",
        type=str,
        help="Threshold for skipped tests (e.g. 'lt:20')",
    )

    # ------------------------------------------------
    # Command: pyproject
    # ------------------------------------------------
    pyproject_parser = subparsers.add_parser(
        "pyproject", help="Operate on pyproject.toml dependencies"
    )
    pyproject_parser.add_argument(
        "--pyproject", required=True, help="Path to the pyproject.toml file"
    )
    pyproject_parser.add_argument(
        "--update-version",
        type=str,
        help="Update local dependency versions to this version",
    )

    # ------------------------------------------------
    # Dispatch Commands
    # ------------------------------------------------
    args = parser.parse_args()

    if args.command == "lock":
        poetry_ops.poetry_lock(directory=args.directory, file=args.file)

    elif args.command == "install":
        poetry_ops.poetry_install(
            directory=args.directory,
            file=args.file,
            extras=args.extras,
            with_dev=args.dev,
            all_extras=args.all_extras,
        )

    elif args.command == "build":
        poetry_ops.recursive_build(directory=args.directory, file=args.file)

    elif args.command == "version":
        version_ops.bump_or_set_version(
            args.pyproject_file, bump=args.bump, set_ver=args.set_ver
        )

    elif args.command == "remote":
        if args.remote_cmd == "fetch":
            ver = remote_ops.fetch_remote_pyproject_version(
                git_url=args.git_url, branch=args.branch, subdirectory=args.subdir
            )
            if ver:
                print(f"Fetched remote version: {ver}")
            else:
                print("Failed to fetch remote version.")
        elif args.remote_cmd == "update":
            success = remote_ops.update_and_write_pyproject(args.input, args.output)
            if not success:
                sys.exit(1)

    elif args.command == "test":
        # Run pytest (with optional parallelism if --num-workers > 1)
        poetry_ops.run_pytests(
            test_directory=args.directory, num_workers=args.num_workers
        )

    elif args.command == "analyze":
        test_ops.analyze_test_file(
            file_path=args.file,
            required_passed=args.required_passed,
            required_skipped=args.required_skipped,
        )

    elif args.command == "pyproject":
        print("Extracting dependencies from pyproject.toml ...")
        paths = pyproject_ops.extract_path_dependencies(args.pyproject)
        if paths:
            print("Local (path) dependencies:")
            print(", ".join(paths))
        else:
            print("No local path dependencies found.")

        git_deps = pyproject_ops.extract_git_dependencies(args.pyproject)
        if git_deps:
            print("\nGit dependencies:")
            for name, details in git_deps.items():
                print(f"{name}: {details}")
        else:
            print("No Git dependencies found.")

        if args.update_version:
            print(f"\nUpdating local dependency versions to {args.update_version} ...")
            pyproject_ops.update_dependency_versions(
                args.pyproject, args.update_version
            )

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
