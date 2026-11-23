from textwrap import dedent

import pytest

from cayaml import YamlParseError, loads, round_trip_dumps, round_trip_loads
from cayaml.ast_nodes import MappingNode, SequenceNode


def test_yaml_12_core_schema_does_not_resolve_yaml_11_boolean_words():
    data = loads(
        dedent(
            """
            true_value: true
            false_value: false
            legacy_words: [yes, no, on, off, y, n]
            nulls: [null, Null, NULL, ~]
            """
        )
    )

    assert data["true_value"] is True
    assert data["false_value"] is False
    assert data["legacy_words"] == ["yes", "no", "on", "off", "y", "n"]
    assert data["nulls"] == [None, None, None, None]


def test_yaml_12_core_schema_integer_forms():
    data = loads(
        dedent(
            """
            decimal: 010
            signed_decimal: +010
            negative_decimal: -010
            binary: 0b1010
            octal: 0o12
            hex: 0x0A
            separated: 1_000_000
            explicit_decimal: !!int "010"
            """
        )
    )

    assert data == {
        "decimal": 10,
        "signed_decimal": 10,
        "negative_decimal": -10,
        "binary": 10,
        "octal": 10,
        "hex": 10,
        "separated": 1_000_000,
        "explicit_decimal": 10,
    }


def test_yaml_12_core_schema_float_forms():
    data = loads(
        dedent(
            """
            decimal: 1.25
            exponent: +1.2e-3
            separated: 1_000.25
            positive_inf: .inf
            negative_inf: -.inf
            nan: .nan
            explicit: !!float "1_000.25"
            """
        )
    )

    assert data["decimal"] == 1.25
    assert data["exponent"] == 0.0012
    assert data["separated"] == 1000.25
    assert data["positive_inf"] == float("inf")
    assert data["negative_inf"] == float("-inf")
    assert str(data["nan"]) == "nan"
    assert data["explicit"] == 1000.25


def test_invalid_explicit_integer_forms_report_parse_errors():
    for source in ("value: !!int 0o8\n", "value: !!int 0b102\n"):
        with pytest.raises(YamlParseError, match="tag !!int"):
            loads(source)


def test_malformed_quoted_scalars_report_parse_errors():
    for source in (
        'value: "unterminated\n',
        "value: 'unterminated\n",
        'value: ["unterminated]\n',
        "value: {'unterminated: value}\n",
    ):
        with pytest.raises(YamlParseError, match="quoted scalar"):
            loads(source)


def test_explicit_seq_and_map_tags_validate_node_kind():
    doc = round_trip_loads(
        dedent(
            """
            sequence: !!seq [a, b]
            mapping: !!map {a: 1, b: 2}
            """
        )
    )

    assert isinstance(doc.root.pairs[0][1], SequenceNode)
    assert doc.root.pairs[0][1].tag == "tag:yaml.org,2002:seq"
    assert doc["sequence"] == ["a", "b"]
    assert isinstance(doc.root.pairs[1][1], MappingNode)
    assert doc.root.pairs[1][1].tag == "tag:yaml.org,2002:map"
    assert doc["mapping"] == {"a": 1, "b": 2}
    assert "!!seq [a, b]" in round_trip_dumps(doc)
    assert "!!map {a: 1, b: 2}" in round_trip_dumps(doc)


@pytest.mark.parametrize(
    "yaml_text,error_match",
    [
        ("bad: !!seq scalar\n", "tag !!seq"),
        ("bad: !!map [not, map]\n", "tag !!map"),
    ],
)
def test_explicit_collection_tags_reject_wrong_node_kind(
    yaml_text, error_match
):
    with pytest.raises(YamlParseError, match=error_match):
        loads(yaml_text)


def test_flow_collections_allow_trailing_commas_and_comments():
    data = loads(
        dedent(
            """
            seq: [a, b, c,] # trailing comma in sequence
            map: {a: 1, b: 2,} # trailing comma in mapping
            nested: [
              {name: alpha, values: [1, 2,]},
              {name: beta, values: [3, 4,]}, # item comment
            ]
            """
        )
    )

    assert data["seq"] == ["a", "b", "c"]
    assert data["map"] == {"a": 1, "b": 2}
    assert data["nested"] == [
        {"name": "alpha", "values": [1, 2]},
        {"name": "beta", "values": [3, 4]},
    ]


def test_json_compatible_flow_mapping_without_spaces_after_colons():
    data = loads(
        dedent(
            """
            json: {
              "name":"alpha",
              "values":[1,2],
              "flags":{"ok":true,"none":null}
            }
            urls: [http://example.test/a, https://example.test/b]
            """
        )
    )

    assert data["json"] == {
        "name": "alpha",
        "values": [1, 2],
        "flags": {"ok": True, "none": None},
    }
    assert data["urls"] == [
        "http://example.test/a",
        "https://example.test/b",
    ]


def test_flow_mapping_colon_before_separator_resolves_empty_value():
    data = loads(
        dedent(
            """
            flow: {empty:, next: value}
            """
        )
    )

    assert data["flow"] == {"empty": None, "next": "value"}


def test_double_quoted_yaml_escape_set():
    data = loads(
        dedent(
            r"""
            escapes: "\0\a\b\t\n\v\f\r\e\"\/\\\x41\u0042\U00000043"
            named: "\N \_ \L \P"
            """
        )
    )

    assert data["escapes"] == ("\0\a\b\t\n\v\f\r\x1b" + '"/\\' + "ABC")
    assert data["named"] == "\u0085 \u00a0 \u2028 \u2029"


def test_invalid_double_quoted_escape_reports_parse_error():
    with pytest.raises(YamlParseError, match="escape"):
        loads('bad: "\\q"\n')


@pytest.mark.parametrize(
    "yaml_text",
    [
        'bad: "\\x1"\n',
        'bad: "\\xG0"\n',
        'bad: "\\u123"\n',
        'bad: "\\u00ZZ"\n',
        'bad: "\\U00110000"\n',
    ],
)
def test_invalid_double_quoted_numeric_escapes_report_parse_errors(
    yaml_text,
):
    with pytest.raises(YamlParseError, match="escape"):
        loads(yaml_text)
