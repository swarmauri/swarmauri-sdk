from pathlib import Path

import toml

from swm_example_community_package import __version__


def test_package_version_matches_pyproject() -> None:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    project_version = toml.load(pyproject_path)["project"]["version"]
    assert __version__ == project_version
