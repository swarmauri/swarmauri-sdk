from PIL import Image
import pytest
from swarmauri.community.tools.concrete.QrCodeGeneratorTool import QrCodeGeneratorTool as Tool

@pytest.mark.unit
def test_name():
    tool = Tool()
    assert tool.name == 'QrCodeGeneratorTool'

@pytest.mark.unit
def test_type():
    assert Tool().type == 'QrCodeGeneratorTool'

@pytest.mark.unit
def test_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "test_data, expected_filename, expected_size",
    [
        ("https://example.com", "test_qr_code_1.png", (330, 330)),  # Adjust expected sizes if necessary
        ("Hello World", "test_qr_code_2.png", (290, 290)),
        ("1234567890", "test_qr_code_3.png", (290, 290)),
    ]
)

@pytest.mark.unit
def test_call(tmp_path, test_data, expected_filename, expected_size):
    tool = Tool()
    output_file = tmp_path / expected_filename

    tool(test_data, str(output_file))

    assert output_file.exists(), "The output file was not created."

    img = Image.open(output_file)
    assert img.format == "PNG", "The generated file is not in PNG format."
    assert img.size == expected_size, "The generated QR code image has unexpected dimensions."

    img.close()
