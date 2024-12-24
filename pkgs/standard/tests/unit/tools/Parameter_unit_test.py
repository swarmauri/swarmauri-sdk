import pytest
from swarmauri.tools.concrete import Parameter

@pytest.mark.unit
def test_ubc_resource():
    parameter = Parameter(
        name="program",
        type="string",
        description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
        required=True,
        enum=["notepad", "calc", "mspaint"]
    )
    assert parameter.resource == 'Parameter'
