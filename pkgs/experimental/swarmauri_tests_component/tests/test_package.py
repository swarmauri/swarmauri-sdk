"""Verify the component conformance package's public and plugin surfaces."""

from importlib.metadata import entry_points, version

from swarmauri_tests_component import ComponentSpec, PROOFS


def test_public_contract_is_importable():
    """Expose the declaration type and the canonical five-proof set."""
    assert ComponentSpec.__name__ == "ComponentSpec"
    assert PROOFS == (
        "construction",
        "identity",
        "resource",
        "serialization",
        "registration",
    )


def test_distribution_version_and_pytest_entry_point():
    """Publish valid version metadata and one loadable pytest11 entry point."""
    assert version("swarmauri_tests_component") == "0.1.0.dev1"
    matches = [
        entry
        for entry in entry_points(group="pytest11")
        if entry.name == "swarmauri_tests_component"
    ]
    assert len(matches) == 1
    assert matches[0].load().__name__ == "swarmauri_tests_component"
