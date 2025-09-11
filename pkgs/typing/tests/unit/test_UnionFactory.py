from typing import Annotated, Any, Union, get_args, get_origin

import time
import pytest

from swarmauri_typing.UnionFactory import UnionFactory, UnionFactoryMetadata


# Test classes
class A:
    pass


class B(A):
    pass


class C:
    pass


# Mock type getters for testing
def get_types_by_class(cls_or_name):
    """Mock function that returns different types based on input"""
    if cls_or_name == "A" or (
        hasattr(cls_or_name, "__name__") and cls_or_name.__name__ == "A"
    ):
        return [A, B]
    elif cls_or_name == "B" or (
        hasattr(cls_or_name, "__name__") and cls_or_name.__name__ == "B"
    ):
        return [B]
    elif cls_or_name == "empty":
        return []
    else:
        return [A, B, C]


class CustomMetadata:
    """Custom metadata for testing annotation extenders"""

    def __init__(self, value):
        self.value = value


def test_union_factory_with_class_input():
    """Test UnionFactory with a class as input"""
    factory = UnionFactory(get_types_by_class)
    result = factory[A]

    # Check that result is an Annotated type
    assert get_origin(result) == Annotated

    args = get_args(result)
    # First argument should be Union[A, B]
    assert args[0] == Union[A, B]

    # Verify metadata
    assert isinstance(args[1], UnionFactoryMetadata)
    assert args[1].data == "A"
    assert args[1].name == "UnionFactory"


def test_union_factory_with_string_input():
    """Test UnionFactory with a string as input"""
    factory = UnionFactory(get_types_by_class)
    result = factory["B"]

    assert get_origin(result) == Annotated

    args = get_args(result)
    # Only B should be in the union
    assert args[0] == Union[B]

    # Verify metadata
    assert isinstance(args[1], UnionFactoryMetadata)
    assert args[1].data == "B"


def test_union_factory_with_empty_result():
    """Test UnionFactory when no types are returned"""
    factory = UnionFactory(get_types_by_class)
    result = factory["empty"]

    assert get_origin(result) == Annotated

    args = get_args(result)
    # Should fallback to Any
    assert args[0] == Any

    # Verify metadata
    assert isinstance(args[1], UnionFactoryMetadata)
    assert args[1].data == "empty"


def test_union_factory_with_custom_name():
    """Test UnionFactory with custom name"""
    factory = UnionFactory(get_types_by_class, name="CustomUnion")
    result = factory[C]

    args = get_args(result)
    # Verify metadata name
    assert args[1].name == "CustomUnion"


def test_union_factory_with_annotation_extenders():
    """Test UnionFactory with additional metadata"""
    custom_metadata1 = CustomMetadata("extra1")
    custom_metadata2 = CustomMetadata("extra2")

    factory = UnionFactory(
        get_types_by_class, annotation_extenders=[custom_metadata1, custom_metadata2]
    )
    result = factory[A]

    args = get_args(result)
    # Should have 3 metadata items: UnionFactoryMetadata and 2 custom ones
    assert len(args) == 4
    assert isinstance(args[1], UnionFactoryMetadata)
    assert args[2] == custom_metadata1
    assert args[3] == custom_metadata2


def test_add_metadata_to_bare_type():
    """Test _add_metadata method with a bare type"""
    factory = UnionFactory(get_types_by_class)
    metadata = CustomMetadata("test")

    # Use the internal method directly
    result = factory._add_metadata(int, metadata)

    assert get_origin(result) == Annotated
    args = get_args(result)
    assert args[0] is int
    assert args[1] == metadata


def test_add_metadata_to_annotated_type():
    """Test _add_metadata method with an already Annotated type"""
    factory = UnionFactory(get_types_by_class)
    base_type = Annotated[str, CustomMetadata("first"), CustomMetadata("second")]
    new_metadata = CustomMetadata("third")

    # Add another metadata to existing Annotated type
    result = factory._add_metadata(base_type, new_metadata)

    assert get_origin(result) == Annotated
    args = get_args(result)
    assert args[0] is str
    assert len(args) == 4
    assert isinstance(args[1], CustomMetadata)
    assert args[1].value == "first"
    assert isinstance(args[2], CustomMetadata)
    assert args[2].value == "second"


@pytest.mark.perf
def test_union_factory_performance_happy_path():
    """Ensure creating unions in happy path performs efficiently"""
    factory = UnionFactory(get_types_by_class)
    start = time.perf_counter()
    for _ in range(1000):
        factory[A]
    duration = time.perf_counter() - start
    assert duration < 0.05


@pytest.mark.perf
def test_union_factory_performance_worst_case():
    """Ensure creating unions with empty result stays performant"""
    factory = UnionFactory(get_types_by_class)
    start = time.perf_counter()
    for _ in range(1000):
        factory["empty"]
    duration = time.perf_counter() - start
    assert duration < 0.05
