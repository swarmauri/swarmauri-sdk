import pytest

from jaml import round_trip_loads

# The input JML content (as a multi-line string)
JML_INPUT = r"""
rootDir = "src"

[test]
module = { name = "example" }
name = %{module.name} + ".py"
path = @{rootDir} + "/" + %{module.name} + "/" + %{name}
type = "python"
test_conf = { testFramework = "pytest", tests = %{module.name} }

"""


# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0011b
def test_context_scoped_var_resolve():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert data["test"]["module"]["name"] == "example"

    resolved_config = data.resolve(data)
    assert resolved_config["test"]["name"] == "example.py"

    rendered_data = data.render(context={})
    print("\n\n\n\n[rendered_data]:")
    print(rendered_data)
    assert rendered_data["rootDir"] == "src"
    assert rendered_data["test"]["name"] == "example.py"
