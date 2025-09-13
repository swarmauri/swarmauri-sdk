#!/usr/bin/env python3
"""Add standard badges to package README files lacking them."""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PKGS_DIR = REPO_ROOT / "pkgs"

BADGE_TEMPLATE = (
    '<p align="center">\n'
    '    <a href="https://pypi.org/project/{name}/">\n'
    '        <img src="https://img.shields.io/pypi/dm/{name}" alt="PyPI - Downloads"/></a>\n'
    '    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/{repo_path}/">\n'
    '        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/{repo_path}.svg"/></a>\n'
    '    <a href="https://pypi.org/project/{name}/">\n'
    '        <img src="https://img.shields.io/pypi/pyversions/{name}" alt="PyPI - Python Version"/></a>\n'
    '    <a href="https://pypi.org/project/{name}/">\n'
    '        <img src="https://img.shields.io/pypi/l/{name}" alt="PyPI - License"/></a>\n'
    '    <a href="https://pypi.org/project/{name}/">\n'
    '        <img src="https://img.shields.io/pypi/v/{name}?label={name}&color=green" alt="PyPI - {name}"/></a>\n'
    "</p>\n"
)


def add_badges(pkg_dir: Path) -> bool:
    readme = pkg_dir / "README.md"
    pyproject = pkg_dir / "pyproject.toml"
    if not readme.exists() or not pyproject.exists():
        return False

    content = readme.read_text(encoding="utf-8")
    if "img.shields.io" in content:
        return False

    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project_name = data.get("project", {}).get("name") or data.get("tool", {}).get(
        "poetry", {}
    ).get("name")
    if not project_name:
        return False
    repo_path = pkg_dir.relative_to(REPO_ROOT).as_posix()
    badge_block = BADGE_TEMPLATE.format(name=project_name, repo_path=repo_path)

    lines = content.splitlines(keepends=True)

    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("![") or "Swamauri Logo" in line:
            insert_idx = i + 1
            while insert_idx < len(lines) and lines[insert_idx].strip() == "":
                insert_idx += 1
            break
        if line.startswith("#"):
            insert_idx = i + 1
            break
    new_content = (
        "".join(lines[:insert_idx])
        + "\n"
        + badge_block
        + "\n---\n\n"
        + "".join(lines[insert_idx:])
    )
    readme.write_text(new_content, encoding="utf-8")
    print(f"Added badges to {readme}")
    return True


def main():
    for pyproject in PKGS_DIR.rglob("pyproject.toml"):
        pkg_dir = pyproject.parent
        if pkg_dir == PKGS_DIR:
            continue
        add_badges(pkg_dir)


if __name__ == "__main__":
    main()
