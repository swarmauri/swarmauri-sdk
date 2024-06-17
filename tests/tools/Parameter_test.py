import pytest
from swarmauri.standard.tools.concrete.Parameter import Parameter

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        parameter = Parameter(
            name="program",
            type="string",
            description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
            required=True,
            enum=["notepad", "calc", "mspaint"]
        )
        assert parameter.resource == 'Parameter'
    test()
