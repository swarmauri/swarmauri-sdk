from typing import List, Optional, Union, Dict, Any
from swarmauri_standard.utils.method_signature_extractor_decorator import (
    MethodSignatureExtractor,
    extract_method_signature,
)


# Test functions with various signature types
def simple_function(x: int, y: str):
    return x, y


def optional_function(a: Optional[int] = None, b: str = "default"):
    return a, b


def list_function(items: List[str], count: int = 1):
    return items, count


def union_function(value: Union[int, str]):
    return value


def complex_function(
    x: int, y: Optional[List[float]] = None, z: Union[str, Dict[str, Any]] = "default"
):
    return x, y, z


class TestMethodSignatureExtractor:
    def test_simple_function_extraction(self):
        """Test extraction of a simple function with basic types"""
        extractor = MethodSignatureExtractor(method=simple_function)

        assert len(extractor.parameters) == 2

        # Check first parameter
        assert extractor.parameters[0].name == "x"
        assert extractor.parameters[0].type == "integer"
        assert extractor.parameters[0].required is True

        # Check second parameter
        assert extractor.parameters[1].name == "y"
        assert extractor.parameters[1].type == "string"
        assert extractor.parameters[1].required is True

    def test_optional_function_extraction(self):
        """Test extraction of a function with optional parameters"""
        extractor = MethodSignatureExtractor(method=optional_function)

        assert len(extractor.parameters) == 2

        # Check first parameter (optional)
        assert extractor.parameters[0].name == "a"
        assert extractor.parameters[0].type == "integer"
        assert extractor.parameters[0].required is False

        # Check second parameter (with default)
        assert extractor.parameters[1].name == "b"
        assert extractor.parameters[1].type == "string"
        assert extractor.parameters[1].required is False

    def test_list_function_extraction(self):
        """Test extraction of a function with list parameter"""
        extractor = MethodSignatureExtractor(method=list_function)

        assert len(extractor.parameters) == 2

        # Check first parameter (list)
        assert extractor.parameters[0].name == "items"
        assert extractor.parameters[0].type == "array"
        assert extractor.parameters[0].required is True

        # Check second parameter (with default)
        assert extractor.parameters[1].name == "count"
        assert extractor.parameters[1].type == "integer"
        assert extractor.parameters[1].required is False

    def test_union_function_extraction(self):
        """Test extraction of a function with union type"""
        extractor = MethodSignatureExtractor(method=union_function)

        assert len(extractor.parameters) == 1

        # Check union parameter
        assert extractor.parameters[0].name == "value"
        assert extractor.parameters[0].type is not None
        assert len(extractor.parameters[0].type) == 2

    def test_complex_function_extraction(self):
        """Test extraction of a function with multiple complex types"""
        extractor = MethodSignatureExtractor(method=complex_function)

        assert len(extractor.parameters) == 3

        # Check first parameter
        assert extractor.parameters[0].name == "x"
        assert extractor.parameters[0].type == "integer"
        assert extractor.parameters[0].required is True

        # Check second parameter (optional list)
        assert extractor.parameters[1].name == "y"
        assert extractor.parameters[1].type == "array"
        assert extractor.parameters[1].required is False

        # Check third parameter (union type with default)
        assert extractor.parameters[2].name == "z"
        assert extractor.parameters[2].type is not None
        assert extractor.parameters[2].required is False

    def test_decorator_signature_extraction(self):
        """Test the extract_method_signature decorator"""

        @extract_method_signature
        def test_decorator_func(a: int, b: Optional[str] = None):
            pass

        # Check if signature_details is added to the function
        assert hasattr(test_decorator_func, "signature_details")

        # Verify the details
        details = test_decorator_func.signature_details
        assert len(details) == 2

        # First parameter
        assert details[0].name == "a"
        assert details[0].type == "integer"
        assert details[0].required is True

        # Second parameter
        assert details[1].name == "b"
        assert details[1].type == "string"
        assert details[1].required is False

    def test_type_mapping(self):
        """Test the type mapping functionality"""
        extractor = MethodSignatureExtractor(method=simple_function)

        # Check predefined type mappings
        type_mapping = extractor._type_mapping
        assert type_mapping[int] == "integer"
        assert type_mapping[float] == "number"
        assert type_mapping[str] == "string"
        assert type_mapping[bool] == "boolean"
        assert type_mapping[list] == "array"
        assert type_mapping[dict] == "object"
        assert type_mapping[Any] == "any"


# Additional edge case tests
def test_empty_function():
    """Test function with no parameters"""

    def empty_func():
        pass

    extractor = MethodSignatureExtractor(method=empty_func)
    assert len(extractor.parameters) == 0


def test_method_with_self():
    """Test method of a class with self parameter"""

    class TestClass:
        def method(self, x: int):
            return x

    extractor = MethodSignatureExtractor(method=TestClass.method)
    assert len(extractor.parameters) == 1
    assert extractor.parameters[0].name == "x"
    assert extractor.parameters[0].type == "integer"
