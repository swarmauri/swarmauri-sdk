from unittest.mock import MagicMock, patch
import base64

import pytest
from swarmauri_tool_folium.FoliumTool import FoliumTool as Tool


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
    "map_center, markers",
    [
        ((37.7749, -122.4194), [(37.7749, -122.4194, "Marker 1")]),
        ((40.7128, -74.0060), [(40.7128, -74.0060, "NYC")]),
        ((34.0522, -118.2437), []),  # No markers case
    ],
)
@pytest.mark.unit
def test_call(map_center, markers):
    tool = Tool()

    # Mock the folium.Map class and related methods
    with patch("folium.Map") as MockMap:
        mock_map_instance = MockMap.return_value
        mock_map_instance.save = MagicMock()

        # Simulate a BytesIO object for the map image
        with patch("io.BytesIO") as MockBytesIO:
            mock_bytes_io = MagicMock()
            mock_bytes_io.getvalue.return_value = b"test_image_data"
            MockBytesIO.return_value = mock_bytes_io

            # Call the tool method
            result = tool(map_center, markers)

            # Assert that the result is a dictionary
            assert isinstance(result, dict), "The result should be a dictionary."

            # Expected keys in the result
            expected_keys = {"image_b64"}

            # Verify that the result is a dictionary
            assert isinstance(result, dict), (
                f"Expected dict, but got {type(result).__name__}"
            )

            # Check if the result contains the 'image_b64' key
            assert expected_keys.issubset(result.keys()), (
                f"Expected keys {expected_keys}, but got {result.keys()}"
            )

            # Verify that the value associated with 'image_b64' is a valid base64 string
            try:
                base64.b64decode(result["image_b64"])
            except Exception:
                pytest.fail("The 'image_b64' value should be a valid base64 string.")

            # Assert that the map was created with the correct center and zoom
            MockMap.assert_called_once_with(location=map_center, zoom_start=13)

            # Assert that the map was saved to a BytesIO object
            assert mock_map_instance.save.called, "The map should have been saved."
            mock_map_instance.save.assert_called_once_with(
                mock_bytes_io, close_file=False
            )
