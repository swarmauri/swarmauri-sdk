import pytest
from swarmauri.standard.tools.concrete.QrCodeGeneratorTool import QrCodeGeneratorTool as Tool

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

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_data = {
        'input_text': "Dummy text for QR code generation."
    }
    result = tool(input_data)
    assert isinstance(result, dict)
    assert 'qr_code' in result
    assert isinstance(result['qr_code'], str)
