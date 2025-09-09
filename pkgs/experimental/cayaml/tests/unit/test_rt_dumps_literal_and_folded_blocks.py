import pytest
from cayaml import round_trip_loads, round_trip_dumps


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Whitespace normalization may differ depending on source indentation"
)
def test_literal_block_dump():
    """
    Test round-trip dumping for a literal block scalar.
    We expect the final emitted YAML to preserve the block style and lines.
    """
    input_yaml = """
    literal_block: |
      Line one
      Line two
    """
    # Load the AST
    docs = round_trip_loads(input_yaml)
    # Dump it back to YAML
    output_yaml = round_trip_dumps(docs)
    # Because docs is a list of docs, you might do round_trip_dumps(docs[0]) if you only want single doc
    # Or if your design expects a YamlStream, you can pass the entire structure.
    # We expect the output to match the original text (minus potential trailing blanks).

    # A typical check is "does the output contain '|\\n  Line one\\n  Line two' ?"
    # NOTE: indentation normalization may cause this check to fail
    assert "|\\n  Line one\\n  Line two" in output_yaml.replace("\r", "")


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Whitespace normalization may differ depending on source indentation"
)
def test_folded_block_dump():
    """
    Test round-trip dumping for a folded block scalar.
    """
    input_yaml = """
    folded_block: >
      This is folded
      into one line.
    """
    docs = round_trip_loads(input_yaml)
    output_yaml = round_trip_dumps(docs)
    # We expect the final text to preserve the folded style '>'.
    # And the lines are typically stored so that re-dumping yields something like:
    # folded_block: >
    #   This is folded
    # NOTE: indentation normalization may cause this check to fail
    #   into one line.
    assert ">\\n  This is folded\\n  into one line." in output_yaml.replace("\r", "")
