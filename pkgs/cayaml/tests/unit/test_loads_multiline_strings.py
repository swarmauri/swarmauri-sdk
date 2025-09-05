import pytest
from cayaml import loads


@pytest.mark.xfail(
    reason="Multi-line strings and different block styles not yet fully supported by cayaml."
)
def test_multiline_strings():
    """
    Tests various forms of multiline string handling:
      - folded (>)
      - literal (|)
      - plain multiline
      - chomping indicators (|-, >+, etc.) which may not be supported
    """
    yaml_str = """
    literal_block: |
      This is on line one.
      This is on line two.

    folded_block: >
      This is line one,
      but folded into
      a single line.

    plain_multiline: This is a \
      single-line string with a backslash in plain style
    """
    data = loads(yaml_str)

    assert data["literal_block"] == "This is on line one.\nThis is on line two.\n"
    assert data["folded_block"] == "This is line one, but folded into a single line.\n"
    assert (
        data["plain_multiline"]
        == "This is a single-line string with a backslash in plain style"
    )
