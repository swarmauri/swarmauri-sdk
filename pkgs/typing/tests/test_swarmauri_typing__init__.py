import swarmauri_typing


def test_all_members():
    """Test that __all__ contains the expected members."""
    expected = {
        "UnionFactory",
        "UnionFactoryMetadata",
        "Intersection",
        "IntersectionMetadata",
    }
    assert set(swarmauri_typing.__all__) == expected


def test_imports():
    """Test that the public classes and metadata can be imported correctly."""
    from swarmauri_typing import (
        UnionFactory,
        UnionFactoryMetadata,
        Intersection,
        IntersectionMetadata,
    )

    # Basic checks to ensure they are imported (more detailed tests should be written for their functionality)
    assert UnionFactory is not None
    assert UnionFactoryMetadata is not None
    assert Intersection is not None
    assert IntersectionMetadata is not None


def test_version():
    """Test that the __version__ attribute exists and is a string."""
    version = swarmauri_typing.__version__
    assert isinstance(version, str)
    # Check that the version is not an empty string.
    assert version != ""
