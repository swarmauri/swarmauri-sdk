import os
from tempfile import NamedTemporaryFile

import pytest
from swarmauri.tools.concrete import MatplotlibCsvTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'MatplotlibCsvTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize(
    "csv_content, x_column, y_column, expected_error",
    [
        (
            "x,y\n1,2\n3,4\n5,6",  # CSV content
            "x",  # x_column
            "y",  # y_column
            None  # No error expected
        ),
        (
            "a,b\n1,2\n3,4\n5,6",  # CSV content
            "x",  # x_column
            "y",  # y_column
            ValueError  # Error expected due to missing columns
        ),
        (
            "x,z\n1,2\n3,4\n5,6",  # CSV content
            "x",  # x_column
            "y",  # y_column
            ValueError  # Error expected due to missing y_column
        )
    ]
)
@pytest.mark.unit
def test_call(csv_content, x_column, y_column, expected_error):
    with NamedTemporaryFile(delete=False, suffix=".csv") as csv_file:
        csv_file.write(csv_content.encode())
        csv_file_path = csv_file.name

    with NamedTemporaryFile(delete=False, suffix=".png") as output_file:
        output_file_path = output_file.name

    tool = Tool()
    expected_keys = {'img_path', 'img_base64', 'data'}

    if expected_error:
        with pytest.raises(expected_error):
            tool(csv_file_path, x_column, y_column, output_file_path)
    else:
        result = tool(csv_file_path, x_column, y_column, output_file_path)
        assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
        assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
        assert isinstance(result.get("data"), list), f"Expected list, but got {type(result).__name__}"
        assert os.path.exists(output_file_path)

    os.remove(csv_file_path)
    if os.path.exists(output_file_path):
        os.remove(output_file_path)