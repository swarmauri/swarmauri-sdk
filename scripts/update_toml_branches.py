import os

from tomlkit import dumps, parse


def update_branch_in_toml(file_path: str) -> None:
    """Update all git dependency branches to 'mono/dev' in a TOML file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc = parse(content)

        # Check for poetry dependencies
        if "tool" in doc and "poetry" in doc["tool"]:
            dependencies = doc["tool"]["poetry"].get("dependencies", {})

            # Update branches in main dependencies
            for dep_name, dep_info in dependencies.items():
                if (
                    isinstance(dep_info, dict)
                    and "git" in dep_info
                    and "branch" in dep_info
                ):
                    if dep_info["branch"].startswith("mono/"):
                        dep_info["branch"] = "mono/dev"
                        print(f"Updated {dep_name} branch to mono/dev in {file_path}")

        # Write changes back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(dumps(doc))

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")


def find_and_update_toml_files(start_path: str) -> None:
    """Recursively find and update all TOML files."""
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(".toml"):
                toml_path = os.path.join(root, file)
                print(f"Processing: {toml_path}")
                update_branch_in_toml(toml_path)


if __name__ == "__main__":
    # Get the base directory of the project
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"Updating TOML files in: {project_dir}")
    find_and_update_toml_files(project_dir)
