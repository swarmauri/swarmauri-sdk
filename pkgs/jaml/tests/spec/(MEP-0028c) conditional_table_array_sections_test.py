import pytest

from jaml import round_trip_loads


# @pytest.mark.xfail(reason="pending validation")
@pytest.mark.spec
@pytest.mark.mep0028c
def test_section_headers_with_clauses():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """

    # The input JML content (as a multi-line string)
    JML_INPUT = r"""
    [["prod" if ${env} == "production" else null]]
    type = "python"


    """

    # The base external context used during rendering.
    BASE_CONTEXT = {"env": "production"}

    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert """"prod" if ${env}=="production" else null""" in data

    resolved_config = data.resolve()
    assert """"prod" if ${env}=="production" else null""" in resolved_config

    # out = data.dumps()
    # rendered_data = data.render(out, context=BASE_CONTEXT)
    rendered_data = data.render(context=BASE_CONTEXT)
    print("\n\n\n\n[RENDERED DATA]:")
    print(rendered_data)
    # assert rendered_data["rootDir"] == "new_src"
    assert "prod" in rendered_data

    final_out = data.dumps()
    print("\n\n\n\n[FINAL_OUT]:")
    print(final_out)
    assert "[[prod]]" in final_out
