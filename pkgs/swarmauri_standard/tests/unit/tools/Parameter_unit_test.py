import pytest
from swarmauri_standard.tools.Parameter import Parameter


@pytest.mark.unit
def test_ubc_resource():
    parameter = Parameter(
        name="program",
        input_type="string",
        description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
        required=True,
        enum=["notepad", "calc", "mspaint"],
    )
    assert parameter.resource == "Parameter"
