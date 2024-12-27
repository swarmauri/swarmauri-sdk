import pytest
from swarmauri.utils.decorate import (
    decorate_cls,
    decorate_instance,
    decorate_instance_method,
)


def decorator_for_testing(func):
    def wrapper(*args, **kwargs):
        return f"Decorated: {func(*args, **kwargs)}"

    return wrapper


@pytest.mark.unit
def test_decorate_cls():
    class TestClass:
        def method1(self):
            return "Method 1"

        def method2(self):
            return "Method 2"

    DecoratedClass = decorate_cls(TestClass, decorator_for_testing)
    instance = DecoratedClass()

    assert instance.method1() == "Decorated: Method 1"
    assert instance.method2() == "Decorated: Method 2"


@pytest.mark.unit
def test_decorate_instance():
    class TestClass:
        def method1(self):
            return "Method 1"

        def method2(self):
            return "Method 2"

    instance = TestClass()
    decorate_instance(instance, decorator_for_testing)

    assert instance.method1() == "Decorated: Method 1"
    assert instance.method2() == "Decorated: Method 2"


@pytest.mark.unit
def test_decorate_cls_non_method_attributes():
    class TestClass:
        class_attr = "I'm a class attribute"

        def method(self):
            return "I'm a method"

    DecoratedClass = decorate_cls(TestClass, decorator_for_testing)
    instance = DecoratedClass()

    assert instance.method() == "Decorated: I'm a method"
    assert (
        DecoratedClass.class_attr == "I'm a class attribute"
    )  # Should remain undecorated


@pytest.mark.unit
def test_decorate_instance_non_method_attributes():
    class TestClass:
        def __init__(self):
            self.instance_attr = "I'm an instance attribute"

        def method(self):
            return "I'm a method"

    instance = TestClass()
    decorate_instance(instance, decorator_for_testing)

    assert instance.method() == "Decorated: I'm a method"
    assert (
        instance.instance_attr == "I'm an instance attribute"
    )  # Should remain undecorated


@pytest.mark.unit
def test_decorate_instance_method_nonexistent():
    class TestClass:
        def method(self):
            return "I'm a method"

    instance = TestClass()

    with pytest.raises(AttributeError):
        decorate_instance_method(instance, "nonexistent_method", decorator_for_testing)
