"""
This file contains the unit tests for the CodeExtractorTool class.

In the CodeExtractorTool, it utilizes ast hence checks for python syntax
Tests created must follow python syntax to avoid errors
"""

import pytest
import tempfile
from swarmauri.standard.tools.concrete.CodeExtractorTool import CodeExtractorTool


@pytest.mark.unit
def test_initialization():
    tool = CodeExtractorTool()
    assert isinstance(tool, CodeExtractorTool)
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_resource():
    """
    Test that the UBC resource attribute is correctly initialized.
    """
    tool = CodeExtractorTool()
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

    tool = CodeExtractorTool()
    extract_documentation = True
    to_be_ignored = ["function1", "variable1"]
    expected_code = """\"\"\" module documentation string\n \"\"\"
print('Hello, World!')"""

    extracted_code = tool(file_name, extract_documentation, to_be_ignored)
    assert extracted_code == expected_code


@pytest.mark.unit
def test_extract_code():
    file_content = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10
print('Hello, World!')"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as file:
        file.write(file_content)
        file_name = file.name

    tool = CodeExtractorTool()
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

    tool = CodeExtractorTool()
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

    tool = CodeExtractorTool()
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

    tool = CodeExtractorTool()
    extract_documentation = True
    to_be_ignored = []

    expected_code = """\"\"\" module documentation string\n \"\"\"
function1 = lambda x: x + 1
variable1 = 10"""

    assert (
        tool.extract_code(file_name, extract_documentation, to_be_ignored)
        == expected_code
    )
