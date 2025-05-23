import pytest

from jaml import round_trip_loads

# The input JML content (as a multi-line string)
JML_INPUT = r"""
["prod" if ${env} == "production" else null]
type = "python"


"""

# The base external context used during rendering.
BASE_CONTEXT = {"env": "production"}

expected_result = r"""
[prod]
type = "python"

"""


# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0028b
def test_conditional_table_header_with_context():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert """"prod" if ${env}=="production" else null""" in data

    data.resolve()
    assert """"prod" if ${env}=="production" else null""" in data
    assert "type" in data[""""prod" if ${env}=="production" else null"""]

    rendered_data = data.render(context=BASE_CONTEXT)
    print("\n\n\n\n[RENDERED DATA]:")
    print(rendered_data)
    assert rendered_data["prod"] == {"type": "python"}

    final_out = data.dumps()
    print("\n\n\n\n[FINAL_OUT]:")
    print(final_out)
    assert "[prod]" in final_out
