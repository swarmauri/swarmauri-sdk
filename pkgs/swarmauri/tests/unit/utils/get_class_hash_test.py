import pytest
from swarmauri.utils.get_class_hash import get_class_hash


@pytest.mark.unit
def test_get_class_hash_basic():
    class TestClass:
        def method1(self):
            pass

        def method2(self, arg):
            pass

    hash1 = get_class_hash(TestClass)
    hash2 = get_class_hash(TestClass)

    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 produces a 64-character hexadecimal string
    assert hash1 == hash2  # Hash should be consistent for the same class


@pytest.mark.unit
def test_get_class_hash_method_order():
    class OrderTest1:
        def method_a(self):
            pass

        def method_b(self):
            pass

    class OrderTest2:
        def method_b(self):
            pass

        def method_a(self):
            pass

    hash1 = get_class_hash(OrderTest1)
    hash2 = get_class_hash(OrderTest2)

    assert hash1 == hash2  # Method order shouldn't affect the hash


@pytest.mark.unit
def test_get_class_hash_with_properties():
    class PropertyTest:
        @property
        def prop(self):
            return 42

        def method(self):
            pass

    hash_value = get_class_hash(PropertyTest)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


@pytest.mark.unit
def test_get_class_hash_inheritance():
    class Parent:
        def parent_method(self):
            pass

    class Child(Parent):
        def child_method(self):
            pass

    parent_hash = get_class_hash(Parent)
    child_hash = get_class_hash(Child)

    assert parent_hash != child_hash


@pytest.mark.unit
def test_get_class_hash_empty_class():
    class EmptyClass:
        pass

    hash_value = get_class_hash(EmptyClass)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64
