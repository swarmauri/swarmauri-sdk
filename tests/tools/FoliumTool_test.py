from unittest.mock import MagicMock, patch

import pytest
from swarmauri.community.tools.concrete.FoliumTool import FoliumTool as Tool

@pytest.mark.unit
def test_name():
    tool = Tool()
    assert tool.name == "FoliumTool"

@pytest.mark.unit
def test_type():
    tool = Tool()
    assert tool.type == "FoliumTool"

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize(
        "map_center, markers, output_file",
        [
            ((37.7749, -122.4194), [(37.7749, -122.4194, "Marker 1")], "test_map_1.html"),
            ((40.7128, -74.0060), [(40.7128, -74.0060, "NYC")], "test_map_2.html"),
            ((34.0522, -118.2437), [], "test_map_3.html"),  # No markers case
        ]
    )


@pytest.mark.unit
def test_call(map_center, markers, output_file):
    tool = Tool()

    with patch('folium.Map') as MockMap:
        mock_map_instance = MockMap.return_value
        mock_map_instance.save = MagicMock()

        tool(map_center, markers, output_file)

        MockMap.assert_called_once_with(location=map_center, zoom_start=13)
        assert mock_map_instance.save.called
        mock_map_instance.save.assert_called_once_with(output_file)


