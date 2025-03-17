#!/usr/bin/env python3
"""
A script to update the entry-points format in TOML files.

Usage:
    python update_entrypoints.py <directory>
"""

import os
import re
import sys
from pathlib import Path


def update_toml_entrypoints(content):
    """
    Updates the entry-points format in TOML content.

    Args:
        content (str): The content of the TOML file

    Returns:
        str: Updated TOML content
    """
    # Match patterns like [tool.project.entry-points."<anything>"] and update
    pattern = r'\[tool\.project\.entry-points\."([^"]+)"\]'
    replacement = r"[project.entry-points.'\1']"

    # Apply the transformation
    updated_content = re.sub(pattern, replacement, content)
    return updated_content


def process_toml_file(file_path):
    """
    Process a single TOML file to update the entry-points format.

    Args:
        file_path (Path): Path to the TOML file

    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        updated_content = update_toml_entrypoints(content)

        if content != updated_content:
            print(f"Updating: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_and_process_toml_files(directory):
    """
    Recursively find and process all TOML files in the specified directory.

    Args:
        directory (str): Directory path to scan

    Returns:
        tuple: (files_processed, files_updated)
    """
    directory_path = Path(directory)
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"Error: {directory} is not a valid directory")
        return 0, 0

    files_processed = 0
    files_updated = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".toml"):
                file_path = Path(root) / file
                files_processed += 1
                if process_toml_file(file_path):
                    files_updated += 1

    return files_processed, files_updated


def main():
    """Main function to run the script."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    files_processed, files_updated = find_and_process_toml_files(directory)

    print("\nSummary:")
    print(f"  TOML files processed: {files_processed}")
    print(f"  TOML files updated: {files_updated}")


if __name__ == "__main__":
    main()
