"""Require Python 3.10 through 3.14 in every Swarmauri project's metadata.

Run with Python >=3.11 and packaging installed. This checks declarations;
runtime compatibility is verified separately with interpreter matrix tests.
"""

from pathlib import Path
import tomllib

from packaging.specifiers import SpecifierSet

VERSIONS = ("3.10", "3.11", "3.12", "3.13", "3.14")


def main():
    root = Path(__file__).resolve().parents[1]
    count = 0
    errors = []
    for path in sorted((root / "pkgs").rglob("pyproject.toml")):
        relative = path.relative_to(root)
        if any(
            part.startswith(".") or part in {"node_modules", "test_project"}
            for part in relative.parts
        ):
            continue
        with path.open("rb") as stream:
            project = tomllib.load(stream).get("project", {})
        if not project.get("name", "").startswith("swarmauri"):
            continue
        count += 1
        declaration = project.get("requires-python", "")
        specifier = SpecifierSet(declaration)
        for version in VERSIONS:
            if not declaration or not specifier.contains(version + ".0"):
                errors.append(f"{relative}: requires-python excludes {version}")
            classifier = f"Programming Language :: Python :: {version}"
            if classifier not in project.get("classifiers", []):
                errors.append(f"{relative}: missing {classifier}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"All {count} Swarmauri projects declare Python 3.10–3.14 support.")


if __name__ == "__main__":
    main()
