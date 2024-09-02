import pytest
from swarmauri.standard.tools.concrete.ParameterTool import ParameterTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    parameter = Tool(
        name="program",
        type="string",
        description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
        required=True,
        enum=["notepad", "calc", "mspaint"]
    )
    assert parameter.resource == 'Parameter'