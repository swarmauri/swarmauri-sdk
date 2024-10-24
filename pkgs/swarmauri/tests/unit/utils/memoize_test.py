import pytest
from swarmauri.utils.memoize import memoize, MemoizingMeta


# Test class using MemoizingMeta
class TestClass(metaclass=MemoizingMeta):
    def expensive_calculation(self, x, y):
        return x + y


@pytest.mark.unit
def test_memoization():
    # Test memoize decorator
    @memoize
    def add(x, y):
        return x + y

    assert add(2, 3) == 5
    assert add(2, 3) == 5  # Should use cached result

    # Test MemoizingMeta
    obj = TestClass()

    # First call
    result1 = obj.expensive_calculation(2, 3)
    assert result1 == 5

    # Second call with same arguments
    result2 = obj.expensive_calculation(2, 3)
    assert result2 == 5

    # Check if the results are the same object (memoized)
    assert result1 is result2


@pytest.mark.unit
def test_memoization_different_args():
    obj = TestClass()

    result1 = obj.expensive_calculation(2, 3)
    result2 = obj.expensive_calculation(3, 4)

    assert result1 == 5
    assert result2 == 7
    assert result1 is not result2


@pytest.mark.unit
def test_memoization_with_different_instances():
    obj1 = TestClass()
    obj2 = TestClass()

    result1 = obj1.expensive_calculation(2, 3)
    result2 = obj2.expensive_calculation(2, 3)

    assert result1 == 5
    assert result2 == 5
