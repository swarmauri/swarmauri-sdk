#!/usr/bin/env python3
import os
import sys

import tomlkit


def update_pyproject_toml(file_path):
    """
    Update a pyproject.toml file to:
    1. Remove [tool.uv.workspace] table and add its members to dependencies
    2. Fix source keys format (remove quotes and parent dirs)
    3. Change dependency-groups format
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            doc = tomlkit.parse(content)

        modified = False

        # Get workspace members before removal
        workspace_members = []
        if "tool" in doc and "uv" in doc["tool"] and "workspace" in doc["tool"]["uv"]:
            if "members" in doc["tool"]["uv"]["workspace"]:
                workspace_members = doc["tool"]["uv"]["workspace"]["members"]

            # Remove workspace table
            del doc["tool"]["uv"]["workspace"]
            modified = True

        # Add dependencies from workspace members
        if workspace_members and "project" in doc:
            if "dependencies" not in doc["project"]:
                doc["project"]["dependencies"] = tomlkit.array()

            existing_deps = [
                dep.split(">=")[0].strip() if isinstance(dep, str) else dep
                for dep in doc["project"]["dependencies"]
            ]

            # Process workspace members
            for member in workspace_members:
                if "/" in member:
                    # Extract last part from path like "standards/swarmauri_embedding_tfidf"
                    package_name = member.split("/")[-1]
                elif member in ["core", "base"]:
                    # Add swarmauri_ prefix
                    package_name = f"swarmauri_{member}"
                else:
                    # Use as is if already has swarmauri prefix
                    package_name = member

                # Add to dependencies if not already there
                if package_name not in existing_deps:
                    doc["project"]["dependencies"].append(package_name)
                    modified = True

        # Fix sources format - remove quotes and fix paths
        if "tool" in doc and "uv" in doc["tool"] and "sources" in doc["tool"]["uv"]:
            old_sources = doc["tool"]["uv"]["sources"]
            new_sources = tomlkit.table()

            for key, value in old_sources.items():
                # Remove quotes and get final part of path
                clean_key = key.strip('"')

                if "/" in clean_key:
                    # Extract last part from path
                    clean_key = clean_key.split("/")[-1]

                # Add swarmauri_ prefix to core packages
                if clean_key in ["core", "base"]:
                    clean_key = f"swarmauri_{clean_key}"

                # Copy the value
                new_sources[clean_key] = value

            # Replace sources table
            doc["tool"]["uv"]["sources"] = new_sources
            modified = True

        # Move dependency-groups from [tool.uv.dependency-groups] to [dependency-groups]
        if (
            "tool" in doc
            and "uv" in doc["tool"]
            and "dependency-groups" in doc["tool"]["uv"]
        ):
            # Get existing dependency groups
            uv_dependency_groups = doc["tool"]["uv"]["dependency-groups"]

            # Create top-level dependency-groups if needed
            if "dependency-groups" not in doc:
                doc["dependency-groups"] = tomlkit.table()
                modified = True

            # Move all dependencies to 'dev' group
            all_deps = tomlkit.array()
            for group_name, deps in uv_dependency_groups.items():
                for dep in deps:
                    if dep not in all_deps:
                        all_deps.append(dep)

            doc["dependency-groups"]["dev"] = all_deps

            # Remove the old dependency-groups
            del doc["tool"]["uv"]["dependency-groups"]
            modified = True

        # Write the updated file only if changes were made
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(doc))
            print(f"✓ Updated {file_path}")
        else:
            print(f"- No changes needed for {file_path}")

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")


def find_and_update_toml_files(directory):
    """Find all *.toml files in the given directory and its subdirectories."""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".toml"):
                file_path = os.path.join(root, file)
                update_pyproject_toml(file_path)
                count += 1

    print(f"\nProcessed {count} TOML files")


if __name__ == "__main__":
    # Get directory from command line or use current directory
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_vectorstore_tfidf"

    print(f"Finding and updating TOML files in {directory}...")
    find_and_update_toml_files(directory)
