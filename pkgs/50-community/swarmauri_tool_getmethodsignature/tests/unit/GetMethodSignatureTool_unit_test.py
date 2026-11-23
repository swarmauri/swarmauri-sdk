import pytest

from swarmauri_tool_getmethodsignature.GetMethodSignatureTool import (
    GetMethodSignatureTool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = GetMethodSignatureTool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert GetMethodSignatureTool().type == "GetMethodSignatureTool"


@pytest.mark.unit
def test_initialization():
    tool = GetMethodSignatureTool()
    assert isinstance(tool.id, str)


@pytest.mark.unit
def test_serialization():
    tool = GetMethodSignatureTool()
    assert (
        tool.id
        == GetMethodSignatureTool.model_validate_json(
            tool.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_call_extracts_signature():
    tool = GetMethodSignatureTool()
    src = "def add(a: int, b: int = 0) -> int:\n    return a + b\n"
    result = tool(source=src, method_name="add")
    assert result["name"] == "add"
    assert result["return_type"] == "int"
    assert result["is_async"] is False
    assert len(result["parameters"]) == 2
    assert result["parameters"][0]["name"] == "a"
    assert result["parameters"][1]["name"] == "b"
    assert result["parameters"][1]["default"] is not None


@pytest.mark.unit
def test_call_method_not_found():
    tool = GetMethodSignatureTool()
    result = tool(source="def f():\n    pass\n", method_name="missing")
    assert "error" in result


@pytest.mark.unit
def test_call_handles_overloads():
    tool = GetMethodSignatureTool()
    src = (
        "def f(x: int) -> int:\n"
        "    return x\n"
        "def f(x: str) -> str:\n"
        "    return x\n"
    )
    result = tool(source=src, method_name="f")
    assert "overloads" in result
    assert len(result["overloads"]) == 2


@pytest.mark.unit
def test_call_no_return_annotation():
    tool = GetMethodSignatureTool()
    result = tool(source="def f(x):\n    pass\n", method_name="f")
    assert result["return_type"] is None


@pytest.mark.unit
def test_call_async_function():
    tool = GetMethodSignatureTool()
    src = "async def f(x: int) -> int:\n    return x\n"
    result = tool(source=src, method_name="f")
    assert result["is_async"] is True


@pytest.mark.unit
def test_call_invalid_source():
    tool = GetMethodSignatureTool()
    result = tool(source="def f(:\n", method_name="f")
    assert "error" in result


@pytest.mark.unit
def test_call_var_args():
    tool = GetMethodSignatureTool()
    src = "def f(a, *args, **kwargs):\n    pass\n"
    result = tool(source=src, method_name="f")
    names = [p["name"] for p in result["parameters"]]
    assert names == ["a", "args", "kwargs"]
    assert result["return_type"] is None


@pytest.mark.unit
def test_call_posonly_args():
    tool = GetMethodSignatureTool()
    src = "def f(x, /, y):\n    pass\n"
    result = tool(source=src, method_name="f")
    names = [p["name"] for p in result["parameters"]]
    assert names == ["x", "y"]


@pytest.mark.unit
def test_call_kwonly_args():
    tool = GetMethodSignatureTool()
    src = "def f(*, x, y=10):\n    pass\n"
    result = tool(source=src, method_name="f")
    params = {p["name"]: p for p in result["parameters"]}
    assert params["x"]["default"] is None
    assert params["y"]["default"] == "10"


@pytest.mark.unit
def test_call_class_method():
    tool = GetMethodSignatureTool()
    src = (
        "class Foo:\n    def method(self, a: int) -> int:\n        return a\n"
    )
    result = tool(source=src, method_name="method")
    names = [p["name"] for p in result["parameters"]]
    assert names == ["self", "a"]
    assert result["return_type"] == "int"


@pytest.mark.unit
def test_call_complex_default():
    tool = GetMethodSignatureTool()
    src = "def f(x=[1, 2, 3]):\n    pass\n"
    result = tool(source=src, method_name="f")
    param = result["parameters"][0]
    assert param["name"] == "x"
    assert param["default"] is not None
