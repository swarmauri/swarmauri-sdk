import math
from textwrap import dedent

from cayaml import dumps, loads, round_trip_dumps, round_trip_loads


def test_flow_collections_and_quoted_scalars():
    flow_seq = (
        "[one, 2, true, null, \"two\\nlines\", 'it''s ok', {nested: [a, b]}]"
    )
    flow_map = '{alpha: 1, beta: [2, 3], gamma: {delta: "value: kept"}}'
    data = loads(
        dedent(
            f"""
            flow_seq: {flow_seq}
            flow_map: {flow_map}
            quoted_hash: "value # not comment"
            single_hash: 'value # not comment'
            """
        )
    )

    assert data["flow_seq"] == [
        "one",
        2,
        True,
        None,
        "two\nlines",
        "it's ok",
        {"nested": ["a", "b"]},
    ]
    assert data["flow_map"] == {
        "alpha": 1,
        "beta": [2, 3],
        "gamma": {"delta": "value: kept"},
    }
    assert data["quoted_hash"] == "value # not comment"
    assert data["single_hash"] == "value # not comment"


def test_inline_sequence_mapping_items():
    data = loads(
        dedent(
            """
            services:
              - name: api
                port: 8080
              - name: worker
                port: 9090
            """
        )
    )

    assert data["services"] == [
        {"name": "api", "port": 8080},
        {"name": "worker", "port": 9090},
    ]


def test_explicit_mapping_keys():
    data = loads(
        dedent(
            """
            ? explicit key
            : explicit value
            ? [compound, key]
            : compound value
            """
        )
    )

    assert data["explicit key"] == "explicit value"
    assert data[("compound", "key")] == "compound value"


def test_block_scalar_chomping_indicators():
    data = loads(
        dedent(
            """
            strip: |-
              line one
              line two
            keep: |+
              line one
              line two

            fold_strip: >-
              folded
              text
            """
        )
    )

    assert data["strip"] == "line one\nline two"
    assert data["keep"] == "line one\nline two\n\n"
    assert data["fold_strip"] == "folded text"


def test_scalar_resolution_for_yaml_core_types():
    data = loads(
        dedent(
            """
            ints: [0b1010, 0x10, 1_000]
            floats: [.inf, -.inf, .nan]
            explicit_str: !!str 42
            explicit_int: !!int "42"
            explicit_float: !!float "3.5"
            explicit_bool: !!bool "true"
            """
        )
    )

    assert data["ints"] == [10, 16, 1000]
    assert data["floats"][0] == math.inf
    assert data["floats"][1] == -math.inf
    assert math.isnan(data["floats"][2])
    assert data["explicit_str"] == "42"
    assert data["explicit_int"] == 42
    assert data["explicit_float"] == 3.5
    assert data["explicit_bool"] is True


def test_alias_identity_and_cycles_in_round_trip_mode():
    doc = round_trip_loads(
        dedent(
            """
            root: &root
              name: cycle
              self: *root
            copy: *root
            """
        )
    )

    root = doc["root"]
    assert doc["copy"] is root
    assert root["self"] is root


def test_round_trip_dumps_new_feature_surface():
    doc = round_trip_loads(
        dedent(
            """
            flow: [a, {b: c}]
            text: |-
              no trailing newline
            tagged: !!str 42
            """
        )
    )

    dumped = round_trip_dumps(doc)
    assert "flow: [a, {b: c}]" in dumped
    assert "text: |-" in dumped
    assert "tagged: !!str 42" in dumped
    assert loads(dumps(loads(dumped)))["flow"] == ["a", {"b": "c"}]
