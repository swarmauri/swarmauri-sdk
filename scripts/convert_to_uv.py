import os
import shutil
import subprocess
from pathlib import Path

import tomlkit


def clean_dependency_spec(spec):
    """Clean dependency specification to make it compatible with UV."""
    if isinstance(spec, str):
        if spec[0].isdigit():
            spec = f"=={spec}"
        # Replace ^ with >=
        spec = spec.replace("^", ">=")
        # Replace * with empty string (or >=0.0.0 if you prefer)
        spec = spec.replace("*", "")
        return spec
    return spec


def convert_to_uv(pyproject_path: Path) -> None:
    """Convert a Poetry pyproject.toml to uv format."""
    # Read the existing pyproject.toml
    with open(pyproject_path, "r") as f:
        data = tomlkit.load(f)

    # Create backup
    backup_path = pyproject_path.parent / "pyproject.bak.toml"
    shutil.copy2(pyproject_path, backup_path)

    # Create new document
    doc = tomlkit.document()

    # Add project table
    project = tomlkit.table()
    poetry_data = data["tool"]["poetry"]

    project["name"] = poetry_data["name"]
    project["version"] = poetry_data["version"]
    project["description"] = poetry_data.get("description", "")
    project["license"] = poetry_data.get("license", "")
    project["readme"] = poetry_data.get("readme", "README.md")
    project["repository"] = poetry_data.get("repository", "")
    project["requires-python"] = poetry_data["dependencies"]["python"]
    project["classifiers"] = poetry_data.get("classifiers", [])

    # Convert authors
    authors = tomlkit.array()
    for author in poetry_data["authors"]:
        author_table = tomlkit.inline_table()
        name, email = author.split("<")
        author_table["name"] = name.strip()
        author_table["email"] = email.strip(">").strip()
        authors.append(author_table)
    project["authors"] = authors

    # Convert regular dependencies
    dependencies = tomlkit.array()
    deps = poetry_data["dependencies"]
    for name, spec in deps.items():
        if name != "python":
            if isinstance(spec, dict):
                if "git" not in spec:
                    # Handle dictionary-style version requirements properly
                    if "version" in spec:
                        fixed_spec = clean_dependency_spec(spec["version"])
                        dependencies.append(f"{name}{fixed_spec}")
                    else:
                        fixed_spec = clean_dependency_spec(spec)
                        dependencies.append(f"{name}{fixed_spec}")
            else:
                # Replace ^ with >= for compatibility
                fixed_spec = (
                    clean_dependency_spec(spec) if isinstance(spec, str) else spec
                )
                dependencies.append(f"{name}{fixed_spec}")
    project["dependencies"] = dependencies

    # Add project table to document
    doc["project"] = project

    # Setup workspace for git dependencies
    workspace = tomlkit.table()
    members = tomlkit.array()
    workspace_members = []  # Track members for later use in sources

    for name, spec in deps.items():
        if isinstance(spec, dict) and "git" in spec:
            if "subdirectory" in spec:
                pkg_path = spec["subdirectory"]
                if pkg_path.startswith("pkgs/"):
                    # Extract the package name from the subdirectory path
                    pkg_name = pkg_path.replace("pkgs/", "")
                    members.append(pkg_name)
                    workspace_members.append(pkg_name)  # Save for sources section

    if members:
        workspace["members"] = members
        uv_table = tomlkit.table()
        uv_table["workspace"] = workspace

        # Create sources section for workspace members
        if workspace_members:
            sources = tomlkit.table()
            for member in workspace_members:
                # Create inline table for each member with workspace = true
                member_source = tomlkit.inline_table()
                member_source["workspace"] = True
                sources[member] = member_source

            uv_table["sources"] = sources

        if "tool" not in doc:
            doc["tool"] = tomlkit.table()
        doc["tool"]["uv"] = uv_table

    # Convert dev dependencies
    if "group" in data["tool"]["poetry"] and "dev" in data["tool"]["poetry"]["group"]:
        dependency_groups = tomlkit.table()
        dev_deps = tomlkit.array()
        lint_deps = tomlkit.array()

        for name, spec in data["tool"]["poetry"]["group"]["dev"][
            "dependencies"
        ].items():
            if name in ["flake8", "ruff"]:
                if isinstance(spec, str):
                    # Replace ^ with >= for compatibility
                    fixed_spec = clean_dependency_spec(spec)
                    print(f"Converting {name} spec: {spec}")
                    lint_deps.append(f"{name}{fixed_spec}")
                else:
                    lint_deps.append(name)
            else:
                if isinstance(spec, str):
                    print(f"Converting {name} spec: {spec}")
                    # Replace ^ with >= for compatibility
                    fixed_spec = clean_dependency_spec(spec)
                    dev_deps.append(f"{name}{fixed_spec}")
                else:
                    dev_deps.append(name)

        # Move dependency groups to [tool.uv.dependency-groups]
        if dev_deps or lint_deps:
            if "tool" not in doc:
                doc["tool"] = tomlkit.table()
            if "uv" not in doc["tool"]:
                doc["tool"]["uv"] = tomlkit.table()

            # Create dependency-groups section under tool.uv
            dependency_groups = tomlkit.table()

            if dev_deps:
                dependency_groups["dev"] = dev_deps
            if lint_deps:
                dependency_groups["lint"] = lint_deps

            doc["tool"]["uv"]["dependency-groups"] = dependency_groups

    # Add build system
    build_system = tomlkit.table()
    build_system["requires"] = ["poetry-core>=1.0.0"]
    build_system["build-backend"] = "poetry.core.masonry.api"
    doc["build-system"] = build_system

    # Create the tool section if it doesn't exist
    if "tool" not in doc:
        doc["tool"] = tomlkit.table()

    # Add updated pytest configuration
    pytest_config = tomlkit.table()
    pytest_config["norecursedirs"] = ["combined", "scripts"]

    # Create the new markers array
    markers = tomlkit.array()
    markers.append("test: standard test")
    markers.append("unit: Unit tests")
    markers.append("i9n: Integration tests")
    markers.append("r8n: Regression tests")
    markers.append("timeout: mark test to timeout after X seconds")
    markers.append("xpass: Expected passes")
    markers.append("xfail: Expected failures")
    markers.append("acceptance: Acceptance tests")

    pytest_config["markers"] = markers
    pytest_config["timeout"] = 300

    # Preserve log settings if they exist
    if (
        "tool" in data
        and "pytest" in data["tool"]
        and "ini_options" in data["tool"]["pytest"]
    ):
        old_pytest = data["tool"]["pytest"]["ini_options"]
        if "log_cli" in old_pytest:
            pytest_config["log_cli"] = old_pytest["log_cli"]
        if "log_cli_level" in old_pytest:
            pytest_config["log_cli_level"] = old_pytest["log_cli_level"]
        if "log_cli_format" in old_pytest:
            pytest_config["log_cli_format"] = old_pytest["log_cli_format"]
        if "log_cli_date_format" in old_pytest:
            pytest_config["log_cli_date_format"] = old_pytest["log_cli_date_format"]
        if "asyncio_default_fixture_loop_scope" in old_pytest:
            pytest_config["asyncio_default_fixture_loop_scope"] = old_pytest[
                "asyncio_default_fixture_loop_scope"
            ]

    doc["tool"]["pytest"] = tomlkit.table()
    doc["tool"]["pytest"]["ini_options"] = pytest_config

    # Preserve other tool configurations
    for tool_name, config in data.get("tool", {}).items():
        if tool_name not in ["poetry", "pytest"]:
            print(f"Preserving {tool_name} configuration")
            doc["tool"][tool_name] = config

    # Handle poetry plugins
    if "plugins" in poetry_data:
        for namespace, plugin_data in poetry_data["plugins"].items():
            entrypoint_group = namespace.strip('"')
            if "tool" not in doc:
                doc["tool"] = tomlkit.table()
            if "project" not in doc["tool"]:
                doc["tool"]["project"] = tomlkit.table()
            if "entry-points" not in doc["tool"]["project"]:
                doc["tool"]["project"]["entry-points"] = tomlkit.table()

            doc["tool"]["project"]["entry-points"][entrypoint_group] = plugin_data

    # Write the new pyproject.toml
    with open(pyproject_path, "w") as f:
        f.write(tomlkit.dumps(doc))
    print(f"Successfully converted {pyproject_path}")


def run_tests(package_path: Path) -> None:
    """Run tests for the converted package."""
    print(f"Running tests for {package_path}")

    try:
        # Install package in development mode with uv
        install_result = subprocess.run(
            ["uv", "pip", "install", "-e", "."],
            cwd=package_path,
            capture_output=True,
            text=True,
        )

        if install_result.returncode != 0:
            print(f"Failed to install package: {install_result.stderr}")
            return

        print("Package installed successfully.")

        # Run pytest
        pytest_result = subprocess.run(
            ["pytest", "-v"], cwd=package_path, capture_output=True, text=True
        )

        print("\nTest Results:")
        print(pytest_result.stdout)

        if pytest_result.returncode != 0:
            print(f"Tests failed with error code {pytest_result.returncode}")
            print(f"Error details: {pytest_result.stderr}")
        else:
            print("All tests passed successfully!")

    except subprocess.SubprocessError as e:
        print(f"Error running tests: {e}")


def find_and_convert_pyproject_files(start_path: str, run_tests_after=False) -> None:
    """Find all pyproject.toml files and convert them to uv format."""
    for root, _, files in os.walk(start_path):
        if "pyproject.toml" in files:
            pyproject_path = Path(root) / "pyproject.toml"
            package_path = Path(root)

            print(f"Converting {pyproject_path}")
            convert_to_uv(pyproject_path)

            if run_tests_after:
                run_tests(package_path)


if __name__ == "__main__":
    # add the project root path
    pkg_list = ["swarmauri_standard", "standards", "community"]
    for pkg in pkg_list:
        project_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), f"../pkgs/{pkg}")
        )
        print(f"Converting pyproject.toml files in: {project_dir}")
        find_and_convert_pyproject_files(project_dir)

    # # Ask if tests should be run after conversion
    # run_tests_option = input("Run tests after conversion? (y/n): ").strip().lower()
    # run_tests_flag = run_tests_option == "y"

    # # Convert all pyproject.toml files
    # find_and_convert_pyproject_files(project_root, run_tests_flag)
