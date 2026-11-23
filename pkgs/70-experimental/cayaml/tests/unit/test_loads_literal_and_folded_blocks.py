from cayaml import loads


def test_literal_block():
    """
    Test literal block scalar (|) formatting.

    Example:
        literal_block: |
          Line one
          Line two
    """
    yaml_str = """
    literal_block: |
      Line one
      Line two
    """
    data = loads(yaml_str)
    # Literal blocks preserve line breaks.
    assert data["literal_block"] == "Line one\nLine two\n"


def test_folded_block():
    """
    Test folded block scalar (>) formatting.

    Example:
        folded_block: >
          This is folded
          into one line.
    """
    yaml_str = """
    folded_block: >
      This is folded
      into one line.
    """
    data = loads(yaml_str)
    # Folded blocks typically join lines into one space-separated line.
    assert data["folded_block"] == "This is folded into one line.\n"
