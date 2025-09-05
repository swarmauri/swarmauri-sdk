import pytest

from jaml import round_trip_loads

# The input JML content (as a multi-line string)
JML_INPUT = r"""
env = "production"

["prod" if @{env} == "production" else null]
type = "python"


"""

expected_result = r"""
[prod]
type = "python"

"""


# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028a
def test_conditional_table_header():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert """"prod" if @{env}=="production" else null""" in data

    data.resolve()
    assert "prod" in data
    assert "type" in data["prod"]

    rendered_data = data.render()
    print("\n\n\n\n[RENDERED DATA]:")
    print(rendered_data)
    assert rendered_data["prod"] == {"type": "python"}

    final_out = data.dumps()
    print("\n\n\n\n[FINAL_OUT]:")
    print(final_out)
    assert "[prod]" in final_out
