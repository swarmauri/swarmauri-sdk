import pytest
from jaml import render


@pytest.mark.unit
def test_render_logical_expression(tmp_path):
    # Create a temporary JML file with a logical expression.
    jml_content = """
[math]
result: int = ~(1 + 2)
    """

    # Render the JML file with an empty context to trigger logical evaluation.
    rendered_output = render(jml_content)

    # The logical expression ~(1 + 2) should evaluate to 3.
    # Check that the evaluated value is present and the original expression is removed.
    assert "3" in rendered_output
    assert "~(" not in rendered_output
