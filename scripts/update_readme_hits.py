#!/usr/bin/env python3

import argparse
import os
import re
from pathlib import Path


def update_readme_hits(readme_path):
    """Update GitHub Hits anchor tag in a README.md file."""
    with open(readme_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Check if the old hits format exists
    old_hits_pattern = r'<a href="https://github\.com/swarmauri/swarmauri-sdk/blob/master/pkgs/[^"]+">.*?hits\.seeyoufarm\.com.*?</a>'
    if not re.search(old_hits_pattern, content, re.DOTALL):
        # Try to find any hits.seeyoufarm.com pattern
        general_hits_pattern = r'<a href="[^"]*">.*?hits\.seeyoufarm\.com.*?</a>'
        if not re.search(general_hits_pattern, content, re.DOTALL):
            print(f"No hits badge to update in {readme_path}")
            return False

    # Get the relative path from the repository root to create the new URL
    rel_path = str(readme_path).replace(os.path.abspath(os.getcwd()), "")
    if rel_path.startswith("/"):
        rel_path = rel_path[1:]

    # Determine the correct GitHub repo path
    dir_path = os.path.dirname(rel_path)
    repo_link = f"github.com/swarmauri/swarmauri-sdk/tree/master/{dir_path}"

    # Create the new anchor tag
    new_hits_tag = f'<a href="https://hits.sh/{repo_link}/">\n        <img alt="Hits" src="https://hits.sh/{repo_link}.svg"/></a>'

    # Replace old hits tags with the new format
    updated_content = re.sub(old_hits_pattern, new_hits_tag, content, flags=re.DOTALL)

    # If the specific pattern wasn't found, try the more general one
    if updated_content == content:
        updated_content = re.sub(
            general_hits_pattern, new_hits_tag, content, flags=re.DOTALL
        )

    # If content was modified, write it back
    if updated_content != content:
        with open(readme_path, "w", encoding="utf-8") as file:
            file.write(updated_content)
        print(f"Updated hits badge in {readme_path}")
        return True

    return False


def scan_directory(base_dir):
    """Scan directory for README.md files and update them."""
    base_path = Path(base_dir)
    updated_count = 0

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower() == "readme.md":
                readme_path = os.path.join(root, file)
                if update_readme_hits(readme_path):
                    updated_count += 1

    return updated_count


def main():
    parser = argparse.ArgumentParser(
        description="Update GitHub Hits badges in README.md files"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for README.md files (default: current directory)",
    )
    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        return 1

    print(f"Scanning {directory} for README.md files...")
    updated_count = scan_directory(directory)

    print(f"Completed! Updated {updated_count} README.md files.")
    return 0


if __name__ == "__main__":
    exit(main())
