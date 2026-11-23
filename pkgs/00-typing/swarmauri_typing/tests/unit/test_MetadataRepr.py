from swarmauri_typing import IntersectionMetadata, UnionFactoryMetadata


class A:
    pass


class B:
    pass


def test_union_factory_metadata_repr():
    """UnionFactoryMetadata should provide informative representation."""
    meta = UnionFactoryMetadata(data="A", name="UF")
    assert repr(meta) == "UnionFactoryMetadata(name='UF', data='A')"


def test_intersection_metadata_repr():
    """IntersectionMetadata __repr__ should include the classes tuple."""
    meta = IntersectionMetadata((A, B))
    expected = f"IntersectionMetadata(classes=({A!r}, {B!r}))"
    assert repr(meta) == expected
