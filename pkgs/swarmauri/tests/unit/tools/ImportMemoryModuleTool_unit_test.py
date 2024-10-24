import pytest
from swarmauri.tools.concrete import ImportMemoryModuleTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'ImportMemoryModuleTool'


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.swm_path) == str
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()
    name_of_new_module = 'test_module'
    code_snippet = "def example_function():" \
        "\t\treturn 'This function is imported from memory.'"

    dot_separated_package_page = "test_package"

    expected_keys = {'message'}

    expected_message = f"{name_of_new_module} has been successfully imported into {dot_separated_package_page}"

    result = tool(name_of_new_module,
                                 code_snippet,
                                 dot_separated_package_page)


    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("message"), str), f"Expected str, but got {type(result).__name__}"

    assert result.get(
        "message") == expected_message, f"Expected Message {expected_message}, but got {result.get('message')}"

    from test_package.test_module import example_function
    assert example_function() == 'This function is imported from memory.'