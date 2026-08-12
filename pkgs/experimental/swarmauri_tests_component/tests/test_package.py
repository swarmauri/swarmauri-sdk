"""Verify the component conformance package's public and plugin surfaces."""

from importlib.metadata import entry_points, version
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

from swarmauri_tests_component import (
    ComponentSpec,
    MethodSpec,
    PROOFS,
    __version__,
    live_session_method_specs,
    model_catalog_method_specs,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    """Read the package version used for the current test run."""
    with (PACKAGE_ROOT / "pyproject.toml").open("rb") as pyproject:
        return tomllib.load(pyproject)["project"]["version"]


def test_public_contract_is_importable():
    """Expose the declaration type and the canonical five-proof set."""
    assert ComponentSpec.__name__ == "ComponentSpec"
    assert MethodSpec.__name__ == "MethodSpec"
    assert callable(live_session_method_specs)
    assert callable(model_catalog_method_specs)
    assert PROOFS == (
        "construction",
        "identity",
        "resource",
        "serialization",
        "registration",
    )


def test_distribution_version_and_pytest_entry_point():
    """Publish valid version metadata and one loadable pytest11 entry point."""
    project_version = _project_version()
    assert version("swarmauri_tests_component") == project_version
    assert __version__ == project_version
    matches = [
        entry
        for entry in entry_points(group="pytest11")
        if entry.name == "swarmauri_tests_component"
    ]
    assert len(matches) == 1
    assert matches[0].load().__name__ == "swarmauri_tests_component"
