import pytest
from swarmauri.utils.apply_metaclass import apply_metaclass_to_cls


@pytest.mark.unit
def test_metaclass_instance():
    class MyMetaclass(type):
        pass

    class MyClass:
        pass

    NewClass = apply_metaclass_to_cls(MyClass, MyMetaclass)
    assert isinstance(NewClass, MyMetaclass)


@pytest.mark.unit
def test_class_name():
    class MyMetaclass(type):
        pass

    class MyClass:
        pass

    NewClass = apply_metaclass_to_cls(MyClass, MyMetaclass)
    assert NewClass.__name__ == MyClass.__name__


@pytest.mark.unit
def test_class_bases():
    class MyMetaclass(type):
        pass

    class MyClass:
        pass

    NewClass = apply_metaclass_to_cls(MyClass, MyMetaclass)
    assert NewClass.__bases__ == MyClass.__bases__


@pytest.mark.unit
def test_original_method_preserved():
    class MyMetaclass(type):
        pass

    class MyClass:
        def original_method(self):
            return "Original method"

    NewClass = apply_metaclass_to_cls(MyClass, MyMetaclass)
    assert hasattr(NewClass, "original_method")
    assert NewClass().original_method() == "Original method"


@pytest.mark.unit
def test_metaclass_modification():
    class MyMetaclass(type):
        def __new__(cls, name, bases, attrs):
            attrs["meta_method"] = lambda self: "Meta method"
            return super().__new__(cls, name, bases, attrs)

    class MyClass:
        pass

    NewClass = apply_metaclass_to_cls(MyClass, MyMetaclass)
    assert hasattr(NewClass(), "meta_method")
    assert NewClass().meta_method() == "Meta method"
