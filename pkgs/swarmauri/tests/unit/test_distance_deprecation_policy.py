import re
from pathlib import Path

import pytest


DISTANCE_PACKAGES = [
    "swarmauri_distance_canberra",
    "swarmauri_distance_chebyshev",
    "swarmauri_distance_chi_squared",
    "swarmauri_distance_cosine",
    "swarmauri_distance_euclidean",
    "swarmauri_distance_haversine",
    "swarmauri_distance_jaccard_index",
    "swarmauri_distance_levenshtein",
    "swarmauri_distance_manhattan",
    "swarmauri_distance_minkowski",
    "swarmauri_distance_sorensen_dice",
    "swarmauri_distance_squared_euclidean",
    "swamauri_metric_wasserstein",
]

DISTANCE_WORKSPACE_PACKAGES = [
    package_name
    for package_name in DISTANCE_PACKAGES
    if package_name != "swamauri_metric_wasserstein"
]

DISTANCE_WORKSPACE_MEMBERS = [
    f'"standards/{package_name}"' for package_name in DISTANCE_WORKSPACE_PACKAGES
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _extract_version_tuple(pyproject_text: str) -> tuple[int, int, int]:
    match = re.search(r'^version = "(\d+)\.(\d+)\.(\d+)', pyproject_text, re.MULTILINE)
    if not match:
        raise AssertionError(
            "Unable to determine Swarmauri version from pyproject.toml"
        )
    return tuple(int(group) for group in match.groups())


@pytest.mark.unit
def test_distance_packages_are_marked_inactive_and_capped():
    root = _repo_root()
    for package_name in DISTANCE_PACKAGES:
        if package_name == "swamauri_metric_wasserstein":
            pyproject = root / "pkgs" / "standards" / package_name / "pyproject.toml"
        else:
            pyproject = root / "pkgs" / "standards" / package_name / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        assert "Development Status :: 7 - Inactive" in text
        assert "<0.10.0" in text


@pytest.mark.unit
def test_distance_package_readmes_include_replacement_guidance():
    root = _repo_root()
    for package_name in DISTANCE_PACKAGES:
        package_dir = root / "pkgs" / "standards" / package_name
        readme = (package_dir / "README.md").read_text(encoding="utf-8")

        assert "Preferred package:" in readme
        assert "https://pypi.org/project/swarmauri_standard/" in readme


@pytest.mark.unit
def test_distance_workspace_members_have_root_sources():
    root = _repo_root()
    root_pyproject = (root / "pkgs" / "pyproject.toml").read_text(encoding="utf-8")

    for member_path in DISTANCE_WORKSPACE_MEMBERS:
        assert member_path in root_pyproject

    for package_name in DISTANCE_WORKSPACE_PACKAGES:
        assert f"{package_name} = {{ workspace = true }}" in root_pyproject

    assert '"deprecated/swarmauri_experimental"' in root_pyproject
    assert "swarmauri_experimental = { workspace = true }" in root_pyproject


@pytest.mark.unit
def test_wasserstein_metric_uses_metric_entry_point_namespace():
    root = _repo_root()
    pyproject = (
        root / "pkgs" / "standards" / "swamauri_metric_wasserstein" / "pyproject.toml"
    ).read_text(encoding="utf-8")

    assert "[project.entry-points.'swarmauri.metrics']" in pyproject
    assert "[project.entry-points.'swarmauri.distances']" not in pyproject


@pytest.mark.unit
def test_distance_packages_removed_by_v0120():
    root = _repo_root()
    swarmauri_pyproject = (root / "pkgs" / "swarmauri" / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    version_tuple = _extract_version_tuple(swarmauri_pyproject)
    if version_tuple < (0, 12, 0):
        pytest.skip("Distance compatibility aliases remain supported before v0.12.0")

    workspace = (root / "pkgs" / "pyproject.toml").read_text(encoding="utf-8")
    interface_registry = (
        root / "pkgs" / "swarmauri" / "swarmauri" / "interface_registry.py"
    ).read_text(encoding="utf-8")
    plugin_registry = (
        root / "pkgs" / "swarmauri" / "swarmauri" / "plugin_citizenship_registry.py"
    ).read_text(encoding="utf-8")

    assert "swarmauri.distances" not in interface_registry
    assert "swarmauri.distances." not in plugin_registry
    for package_name in DISTANCE_PACKAGES:
        assert f"standards/{package_name}" not in workspace
        assert not (root / "pkgs" / "standards" / package_name).exists()
        assert (root / "pkgs" / "deprecated" / package_name).exists()
