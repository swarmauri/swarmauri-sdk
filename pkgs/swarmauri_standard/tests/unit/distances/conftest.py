import re
from pathlib import Path

import pytest


def _extract_version_tuple(pyproject_text: str) -> tuple[int, int, int]:
    match = re.search(
        r'^version = "(\d+)\.(\d+)\.(\d+)', pyproject_text, re.MULTILINE
    )
    if not match:
        raise AssertionError(
            "Unable to determine Swarmauri version from pyproject.toml"
        )
    return tuple(int(group) for group in match.groups())


@pytest.fixture(autouse=True)
def skip_distance_compatibility_tests_after_v0120():
    repo_pkgs = Path(__file__).resolve().parents[4]
    swarmauri_pyproject = (
        repo_pkgs / "swarmauri" / "pyproject.toml"
    ).read_text(encoding="utf-8")
    version_tuple = _extract_version_tuple(swarmauri_pyproject)
    if version_tuple >= (0, 12, 0):
        pytest.skip(
            "Deprecated distance compatibility tests are removed in v0.12.0"
        )
