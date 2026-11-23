from textwrap import dedent

import pytest

from cayaml import YamlParseError, loads


def test_duplicate_block_mapping_keys_are_parse_errors():
    with pytest.raises(YamlParseError, match="duplicate mapping key"):
        loads(
            dedent(
                """
                key: first
                key: second
                """
            )
        )


def test_duplicate_keys_after_scalar_resolution_are_parse_errors():
    with pytest.raises(YamlParseError, match="duplicate mapping key"):
        loads(
            dedent(
                """
                1: decimal
                01: same decimal
                """
            )
        )


def test_duplicate_flow_mapping_keys_are_parse_errors():
    with pytest.raises(YamlParseError, match="duplicate mapping key"):
        loads("{key: first, key: second}")


def test_duplicate_complex_mapping_keys_are_parse_errors():
    with pytest.raises(YamlParseError, match="duplicate mapping key"):
        loads(
            dedent(
                """
                ? [a, b]
                : first
                ? [a, b]
                : second
                """
            )
        )


def test_duplicate_compact_explicit_mapping_keys_are_parse_errors():
    with pytest.raises(YamlParseError, match="duplicate mapping key"):
        loads(
            dedent(
                """
                ? [a, b]: first
                ? [a, b]: second
                """
            )
        )


def test_distinct_complex_mapping_keys_remain_valid():
    data = loads(
        dedent(
            """
            ? [a, b]
            : first
            ? [a, c]
            : second
            """
        )
    )

    assert data == {("a", "b"): "first", ("a", "c"): "second"}
