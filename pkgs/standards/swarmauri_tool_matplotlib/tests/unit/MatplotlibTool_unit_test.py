import os

import pytest
from swarmauri_tool_matplotlib.MatplotlibTool import MatplotlibTool as Tool


@pytest.fixture
def matplotlib_tool():
    return Tool()


@pytest.mark.unit
def test_ubc_resource(tool):
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type(tool):
    assert tool.type == "MatplotlibTool"


@pytest.mark.unit
def test_initialization(tool):
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization(tool):
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "plot_type, x_data, y_data, title, x_label, y_label, save_path",
    [
        (
            "line",
            [1, 2, 3],
            [4, 5, 6],
            "Line Plot",
            "X-axis",
            "Y-axis",
            "test_line_plot.png",
        ),
        (
            "bar",
            [1, 2, 3],
            [4, 5, 6],
            "Bar Plot",
            "X-axis",
            "Y-axis",
            "test_bar_plot.png",
        ),
        (
            "scatter",
            [1, 2, 3],
            [4, 5, 6],
            "Scatter Plot",
            "X-axis",
            "Y-axis",
            "test_scatter_plot.png",
        ),
    ],
)
@pytest.mark.unit
def test_call(plot_type, x_data, y_data, title, x_label, y_label, save_path, tool):
    expected_keys = {"img_path", "img_base64", "data"}

    result = tool(plot_type, x_data, y_data, title, x_label, y_label, save_path)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), (
        f"Expected keys {expected_keys} but got {result.keys()}"
    )
    assert isinstance(result.get("data"), list), (
        f"Expected list, but got {type(result).__name__}"
    )
    assert os.path.exists(save_path)

    os.remove(save_path)
