#!/usr/bin/env python3
"""Verify required files and metadata for all packages.

The script checks each package under ``pkgs/`` for:
- Apache 2.0 ``LICENSE`` file
- ``NOTICE`` file
- ``README.md`` with Swarmauri SVG header and standard badges
- ``pyproject.toml`` listing Jacob Stewart as author
- ``pyproject.toml`` declaring Apache 2.0 license

A markdown report is printed. The script exits with a non-zero status if any
checks fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:  # Python >=3.11
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for Python <3.11
    import tomli as tomllib  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
PKGS_DIR = REPO_ROOT / "pkgs"


def iter_packages() -> list[Path]:
    """Yield directories containing a ``pyproject.toml`` under ``pkgs``."""
    packages: list[Path] = []
    for pyproject in PKGS_DIR.rglob("pyproject.toml"):
        if pyproject.parent == PKGS_DIR:
            # Skip monorepo pyproject
            continue
        packages.append(pyproject.parent)
    return packages


def has_apache_license(pkg_dir: Path) -> bool:
    license_file = pkg_dir / "LICENSE"
    if not license_file.is_file():
        return False
    text = license_file.read_text(encoding="utf-8", errors="ignore")
    return "Apache License" in text and "Version 2.0" in text


def has_notice(pkg_dir: Path) -> bool:
    notice = pkg_dir / "NOTICE"
    return notice.is_file()


def readme_has_header_and_badges(pkg_dir: Path, project_name: str) -> bool:
    readme = pkg_dir / "README.md"
    if not readme.is_file():
        return False
    text = readme.read_text(encoding="utf-8", errors="ignore")
    header_ok = "assets/swarmauri.brand.theme.svg" in text
    rel_path = pkg_dir.relative_to(REPO_ROOT).as_posix()
    badge_patterns = [
        f"https://img.shields.io/pypi/dm/{project_name}",
        f"https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/{rel_path}.svg",
        f"https://img.shields.io/pypi/pyversions/{project_name}",
        f"https://img.shields.io/pypi/l/{project_name}",
        f"https://img.shields.io/pypi/v/{project_name}?label={project_name}&color=green",
    ]
    badges_ok = all(pat in text for pat in badge_patterns)
    return header_ok and badges_ok


def parse_pyproject(pkg_dir: Path) -> tuple[str, bool, bool]:
    pyproject = pkg_dir / "pyproject.toml"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    name = project.get("name", pkg_dir.name)
    authors = project.get("authors", [])
    author_ok = any(
        isinstance(a, dict) and a.get("email") == "jacob@swarmauri.com" for a in authors
    )
    license_field = project.get("license")
    license_ok = False
    if isinstance(license_field, str):
        license_ok = "Apache" in license_field and "2.0" in license_field
    elif isinstance(license_field, dict):
        if "text" in license_field and isinstance(license_field["text"], str):
            txt = license_field["text"]
            license_ok = "Apache" in txt and "2.0" in txt
        elif "file" in license_field and isinstance(license_field["file"], str):
            lf = pkg_dir / license_field["file"]
            if lf.is_file():
                txt = lf.read_text(encoding="utf-8", errors="ignore")
                license_ok = "Apache License" in txt and "Version 2.0" in txt
    return name, author_ok, license_ok


def build_report(rows: list[dict]) -> str:
    header = (
        "| Package | Directory | LICENSE | NOTICE | README | Author | Pyproject License |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    lines = []
    for r in rows:

        def mark(ok: bool) -> str:
            return "✅" if ok else "❌"

        lines.append(
            f"| {r['name']} | {r['directory']} | {mark(r['license_file'])} | "
            f"{mark(r['notice_file'])} | {mark(r['readme'])} | {mark(r['author'])} | "
            f"{mark(r['license_pyproject'])} |"
        )
    return header + "\n".join(lines) + "\n"


def main() -> None:
    packages = sorted(iter_packages())
    rows = []
    has_failures = False
    for pkg in packages:
        name, author_ok, license_pyproject_ok = parse_pyproject(pkg)
        row = {
            "name": name,
            "directory": pkg.relative_to(REPO_ROOT).as_posix(),
            "license_file": has_apache_license(pkg),
            "notice_file": has_notice(pkg),
            "readme": readme_has_header_and_badges(pkg, name),
            "author": author_ok,
            "license_pyproject": license_pyproject_ok,
        }
        if not all(row.values()):
            has_failures = True
        rows.append(row)
    report = build_report(rows)
    print(report)
    if has_failures:
        print(
            "One or more packages are missing required files or metadata.",
            file=sys.stderr,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
