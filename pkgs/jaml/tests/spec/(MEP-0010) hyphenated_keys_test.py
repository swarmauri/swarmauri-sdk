# test_hyphenated_identifiers.py
import pytest

from jaml import (
    round_trip_loads,
    loads,
)


@pytest.mark.spec
@pytest.mark.mep0010
# @pytest.mark.xfail(reason="Hyphenated section name round-trip preservation not fully implemented yet.")
def test_hyphenated_section_name_round_trip():
    """
    MEP-010:
      Hyphenated section names should parse and re-serialize without error.
    """
    toml_str = """
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Check that the section name is preserved
    assert "[build-system]" in reserialized, (
        "Hyphenated section name not preserved in round-trip"
    )


@pytest.mark.spec
@pytest.mark.mep0010
# @pytest.mark.xfail(reason="Hyphenated key name without annotation preservation not fully implemented yet.")
def test_hyphenated_key_name_no_annotation():
    """
    MEP-010:
      A key with a hyphen should parse and preserve the identifier exactly.
    """
    toml_str = """
[project]
build-backend = "poetry.core.masonry.api"
"""
    data = loads(toml_str)
    # Check that the key is recognized
    assert "build-backend" in data["project"], (
        "Hyphenated key name missing from parsed data"
    )
    assert data["project"]["build-backend"] == '"poetry.core.masonry.api"'

    # Now confirm round-trip
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    assert 'build-backend = "poetry.core.masonry.api"' in reserialized


@pytest.mark.spec
@pytest.mark.mep0010
# @pytest.mark.xfail(reason="Hyphenated key name with annotation preservation not fully implemented yet.")
def test_hyphenated_key_name_with_annotation():
    """
    MEP-010:
      A hyphenated key name with a type annotation is valid
      and should be preserved exactly.
    """
    toml_str = """
[project]
build-backend: str = "poetry.core.masonry.api"
"""
    # Round-trip check
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Ensure the key and annotation are present
    assert 'build-backend: str = "poetry.core.masonry.api"' in reserialized


@pytest.mark.spec
@pytest.mark.mep0010
# @pytest.mark.xfail(reason="Combined hyphenated section and key names preservation not fully implemented yet.")
def test_hyphenated_section_and_key_names_together():
    """
    MEP-010:
      It's valid to have both the section name and key name contain hyphens.
    """
    toml_str = """
[my-build-system]
build-backend: str = "poetry.core.masonry.api"
additional-requires = ["something>=1.2.3"]
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Check section
    assert "[my-build-system]" in reserialized
    # Check both keys
    assert 'build-backend: str = "poetry.core.masonry.api"' in reserialized
    assert 'additional-requires = ["something>=1.2.3"]' in reserialized


# @pytest.mark.xfail(reason="Case-preservation for hyphenated identifiers not fully implemented.")
@pytest.mark.spec
@pytest.mark.mep0010
def test_case_preservation_for_hyphenated_identifiers():
    """
    MEP-010 Open Issue:
      Confirm whether we preserve case exactly in hyphenated names.
      If the spec states we do, and it's not yet implemented, we xfail.
    """
    toml_str = """
[Build-System]
my-Key: str = "SomeValue"
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Expect exact case preservation
    assert "[Build-System]" in reserialized, "Section name case changed unexpectedly"
    assert 'my-Key: str = "SomeValue"' in reserialized, (
        "Key name case changed unexpectedly"
    )
