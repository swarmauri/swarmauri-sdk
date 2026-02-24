from __future__ import annotations

from importlib import metadata
from pathlib import Path
import re
import tomllib

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PACKAGE_ROOT / "pyproject.toml"
TRANSPORT_PATTERN = re.compile(r"^(swarmauri_transport_[A-Za-z0-9_]+)")


def _normalize_name(name: str) -> str:
    return name.lower().replace("-", "_")


def _transport_requirements_from_distribution(distribution_name: str) -> set[str]:
    try:
        dist = metadata.distribution(distribution_name)
    except metadata.PackageNotFoundError:
        pytest.skip(f"{distribution_name} is not installed in this environment")

    requirements = dist.requires or []
    transport_requirements: set[str] = set()
    for requirement in requirements:
        match = TRANSPORT_PATTERN.match(requirement.strip())
        if match:
            transport_requirements.add(_normalize_name(match.group(1)))
    return transport_requirements


def _transport_optional_dependencies_from_pyproject() -> set[str]:
    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    transport_dependencies = data["project"]["optional-dependencies"]["transports"]

    package_names: set[str] = set()
    for dependency in transport_dependencies:
        match = TRANSPORT_PATTERN.match(dependency)
        if match:
            package_names.add(_normalize_name(match.group(1)))
    return package_names


def assert_transport_dependency_parity(
    *, transport_package: str, parity_distribution_name: str
) -> None:
    expected_transport_packages = _transport_optional_dependencies_from_pyproject()
    normalized_transport_package = _normalize_name(transport_package)

    assert normalized_transport_package in expected_transport_packages

    swarmauri_canon_http_requirements = _transport_requirements_from_distribution(
        "swarmauri_canon_http"
    )
    parity_requirements = _transport_requirements_from_distribution(
        parity_distribution_name
    )

    assert normalized_transport_package in swarmauri_canon_http_requirements
    assert normalized_transport_package not in parity_requirements
