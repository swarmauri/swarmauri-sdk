from typing import Annotated, Union, get_args, get_origin

import time
import pytest

from swarmauri_typing.IntersectionFactory import (
    IntersectionFactory,
    IntersectionFactoryMetadata,
)


# Test classes
class A:
    pass


class B(A):
    pass


class C:
    pass


class D(B, C):
    pass


def test_intersection_factory_single_class():
    """Test IntersectionFactory with a single class"""
    result = IntersectionFactory[A]

    # Check that result is an Annotated type
    assert get_origin(result) == Annotated

    args = get_args(result)
    # First argument should be Union of A and object
    assert args[0] == Union[A, object]

    # Verify metadata
    assert isinstance(args[1], IntersectionFactoryMetadata)
    assert args[1].classes == (A,)


def test_intersection_factory_compatible_classes():
    """Test IntersectionFactory with classes that have common ancestors"""
    result = IntersectionFactory[B, D]

    assert get_origin(result) == Annotated

    args = get_args(result)
    # B and D share B, A, and object in their MROs
    assert args[0] == Union[B, A, object]

    # Verify metadata
    assert isinstance(args[1], IntersectionFactoryMetadata)
    assert args[1].classes == (B, D)


def test_intersection_factory_disjoint_classes():
    """Test IntersectionFactory with classes that only share object as ancestor"""
    result = IntersectionFactory[A, C]

    assert get_origin(result) == Annotated

    args = get_args(result)
    # Only object is common
    assert args[0] == Union[object]

    # Verify metadata
    assert isinstance(args[1], IntersectionFactoryMetadata)
    assert args[1].classes == (A, C)


def test_intersection_factory_multi_inheritance():
    """Test with classes that have multiple inheritance"""
    result = IntersectionFactory[B, C, D]

    assert get_origin(result) == Annotated

    args = get_args(result)
    # Since D inherits from both B and C, the only common class among all three would be object
    # The ordering follows B's MRO
    assert args[0] == Union[object]

    # Verify metadata
    assert isinstance(args[1], IntersectionFactoryMetadata)
    assert args[1].classes == (B, C, D)


@pytest.mark.perf
def test_intersection_performance_happy_path():
    """Ensure happy path intersection performs efficiently"""
    start = time.perf_counter()
    for _ in range(1000):
        IntersectionFactory[B, D]
    duration = time.perf_counter() - start
    assert duration < 0.05


@pytest.mark.perf
def test_intersection_performance_worst_case():
    """Ensure worst-case intersection performs within bounds"""
    start = time.perf_counter()
    for _ in range(1000):
        IntersectionFactory[A, C]
    duration = time.perf_counter() - start
    assert duration < 0.05
