#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def run_package_tests(package_path: Path, verbose=True):
    """Run tests for a package using uv."""
    package_name = package_path.name
    print(f"\n{'=' * 80}")
    print(f"Testing package: {package_name}")
    print(f"{'=' * 80}")

    try:
        # Create a temporary virtual environment
        venv_path = package_path / ".venv"
        if venv_path.exists():
            print(f"Using existing venv at {venv_path}")
        else:
            print(f"Creating virtual environment at {venv_path}")
            subprocess.run(
                ["uv", "venv", "-p", "python3.11"], cwd=package_path, check=True
            )

        # Install package in development mode with dev dependencies
        print(f"Installing {package_name} with dependencies...")
        install_cmd = ["uv", "pip", "install", "-e", "."]

        # Add verbose flag if requested
        if verbose:
            install_cmd.append("-v")

        install_result = subprocess.run(
            install_cmd, cwd=package_path, capture_output=not verbose, text=True
        )

        if install_result.returncode != 0:
            print(
                f"Failed to install package: {install_result.stderr if not verbose else ''}"
            )
            return False

        # Install test dependencies
        print("Installing test dependencies...")
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "pytest",
                "pytest-asyncio",
                "pytest-xdist",
                "pytest-cov",
            ],
            cwd=package_path,
            capture_output=not verbose,
            text=True,
        )

        # Run pytest with coverage
        print(f"Running tests for {package_name}...")
        test_cmd = ["python", "-m", "pytest", "-xvs", "--cov=."]

        # Run tests
        test_result = subprocess.run(
            test_cmd, cwd=package_path, capture_output=not verbose, text=True
        )

        if not verbose and test_result.returncode != 0:
            print(f"Tests failed for {package_name}")
            print(f"Error details:\n{test_result.stderr}")
            print(f"Output:\n{test_result.stdout}")
            return False

        return test_result.returncode == 0

    except subprocess.SubprocessError as e:
        print(f"Error running tests for {package_name}: {e}")
        return False


def find_and_test_packages(start_path: Path, filter_name=None):
    """Find all packages and run tests."""
    results = {}

    # Find all directories that contain pyproject.toml
    for root, _, files in os.walk(start_path):
        if "pyproject.toml" in files:
            package_path = Path(root)

            # Skip if filter is provided and package name doesn't match
            if filter_name and filter_name.lower() not in package_path.name.lower():
                continue

            # Run tests for this package
            success = run_package_tests(package_path)
            results[package_path.name] = success

    # Print summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = [pkg for pkg, success in results.items() if success]
    failed = [pkg for pkg, success in results.items() if not success]

    print(f"Packages tested: {len(results)}")
    print(f"Passed: {len(passed)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed packages:")
        for pkg in failed:
            print(f"  - {pkg}")

    return len(failed) == 0


if __name__ == "__main__":
    # Get SDK root path
    script_dir = Path(__file__).parent
    sdk_root = script_dir.parent
    pkgs_dir = sdk_root / "pkgs"

    # Check if a filter is provided
    filter_name = sys.argv[1] if len(sys.argv) > 1 else None

    if filter_name:
        print(f"Running tests for packages matching: {filter_name}")
    else:
        print("Running tests for all packages")

    # Run tests
    success = find_and_test_packages(pkgs_dir, filter_name)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
