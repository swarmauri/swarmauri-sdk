"""
This file contains the unit tests for the CodeExtractorTool class.

In the CodeExtractorTool, it utilizes ast hence checks for python syntax
Tests created must follow python syntax to avoid errors
"""
from unittest.mock import patch, mock_open

import pytest
import tempfile
from swarmauri.standard.tools.concrete.CodeExtractorTool import CodeExtractorTool as Tool


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert isinstance(tool, Tool)
    assert tool.resource == "Tool"

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'CodeExtractorTool'

@pytest.mark.unit
def test_ubc_resource():
    """
    Test that the UBC resource attribute is correctly initialized.
    """
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_call():
    """
    Test the __call__ method of CodeExtractorTool.
    """
    file_content = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10
print('Hello, World!')"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as file:
        file.write(file_content)
        file_name = file.name

    tool = Tool()
    extract_documentation = True
    to_be_ignored = ["function1", "variable1"]
    expected_code = """\"\"\" module documentation string\n \"\"\"
print('Hello, World!')"""

    extracted_code = tool(file_name, extract_documentation, to_be_ignored)
    assert extracted_code == expected_code

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_extract_code():
    file_content = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10
print('Hello, World!')"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as file:
        file.write(file_content)
        file_name = file.name

    tool = Tool()
    extract_documentation = True
    to_be_ignored = ["function1", "variable1"]

    expected_code = """\"\"\" module documentation string\n \"\"\"
print('Hello, World!')"""

    assert (
        tool.extract_code(file_name, extract_documentation, to_be_ignored)
        == expected_code
    )


@pytest.mark.unit
def test_extract_code_with_no_ignored_elements():
    file_content = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10
print('Hello, World!')"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as file:
        file.write(file_content)
        file_name = file.name

    tool = Tool()
    extract_documentation = True
    to_be_ignored = []

    assert (
        tool.extract_code(file_name, extract_documentation, to_be_ignored)
        == file_content
    )


@pytest.mark.unit
def test_extract_code_with_no_documentation():
    file_content = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10
print('Hello, World!')"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as file:
        file.write(file_content)
        file_name = file.name

    tool = Tool()
    extract_documentation = False
    to_be_ignored = []

    expected_code = """function1 = lambda x: x + 1
variable1 = 10
print('Hello, World!')"""

    assert (
        tool.extract_code(file_name, extract_documentation, to_be_ignored)
        == expected_code
    )

def test_stop_collecting_lines():
    file_content = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10
# non-essentials
if "#" in stripped_line and "non-essentials" in stripped_line:
    break
print('Hello, World!')"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as file:
        file.write(file_content)
        file_name = file.name

    tool = Tool()
    extract_documentation = True
    to_be_ignored = []

    expected_code = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10"""

    assert (
        tool.extract_code(file_name, extract_documentation, to_be_ignored)
        == expected_code
    )

@pytest.mark.unit
@pytest.mark.parametrize(
    "file_contents, extract_documentation, to_be_ignored, expected_code",
    [
        (
            '''
            """
            This is a docstring.
            """
            def foo():
                pass
            def bar():
                pass
            # non-essentials
            ''',
            True,
            [],
            'def foo():\n    pass\n\ndef bar():\n    pass\n'
        ),
        (
            '''
            """
            This is a docstring.
            """
            def foo():
                pass
            def bar():
                pass
            # non-essentials
            ''',
            False,
            [],
            'def foo():\n    pass\n\ndef bar():\n    pass\n'
        ),
        (
            '''
            """
            This is a docstring.
            """
            def foo():
                pass
            def bar():
                pass
            # non-essentials
            ''',
            True,
            ['foo'],
            'def bar():\n    pass\n'
        ),
        (
            '''
            def foo():
                pass
            def bar():
                pass
            ''',
            True,
            [],
            'def foo():\n    pass\n\ndef bar():\n    pass\n'
        ),
        (
            '''
            def foo():
                pass
            def bar():
                pass
            ''',
            False,
            ['foo'],
            'def bar():\n    pass\n'
        ),
    ]
)
def test_call(file_contents, extract_documentation, to_be_ignored, expected_code):
    tool = Tool()

    expected_keys = {'code'}

    with patch("builtins.open", mock_open(read_data=file_contents)):
        result = tool(file_name="fake_file.py", extract_documentation=extract_documentation, to_be_ignored=to_be_ignored)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("code"), str), f"Expected str, but got {type(result.get('code')).__name__}"
    assert result.get("code") == expected_code, f"Expected Extracted Code {expected_code}, but got {result.get('code')}"