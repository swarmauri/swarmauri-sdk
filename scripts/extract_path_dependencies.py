# scripts/extract_path_dependencies.py
import toml
import argparse
import os
import sys


def extract_path_dependencies(pyproject_path):
    """Extract path dependencies from a pyproject.toml file."""
    with open(pyproject_path, "r") as f:
        data = toml.load(f)

    # Navigate to dependencies
    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})

    # Extract paths
    path_deps = [
        v["path"] for v in dependencies.values() if isinstance(v, dict) and "path" in v
    ]

    return path_deps


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Extract path dependencies from pyproject.toml"
    )
    parser.add_argument(
        "--pyproject", type=str, required=True, help="Path to the pyproject.toml file"
    )

    args = parser.parse_args()

    # Check if the specified pyproject.toml file exists
    if not os.path.isfile(args.pyproject):
        print(f"Error: pyproject.toml not found at {args.pyproject}", file=sys.stderr)
        sys.exit(1)

    # Extract path dependencies
    path_dependencies = extract_path_dependencies(args.pyproject)

    # Output the dependencies in a format GitHub Actions can use
    print(f"{','.join(path_dependencies)}")


if __name__ == "__main__":
    main()
