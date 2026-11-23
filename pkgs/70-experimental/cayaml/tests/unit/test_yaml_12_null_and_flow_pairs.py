from textwrap import dedent

from cayaml import loads, round_trip_dumps, round_trip_loads


def test_empty_block_nodes_resolve_to_null():
    data = loads(
        dedent(
            """
            mapping:
              present:
              explicit: null
            sequence:
              -
              - value
            """
        )
    )

    assert data["mapping"] == {"present": None, "explicit": None}
    assert data["sequence"] == [None, "value"]


def test_empty_flow_mapping_keys_and_values_resolve_to_null():
    data = loads(
        dedent(
            """
            flow: {empty: , : blank-key, explicit: null}
            """
        )
    )

    assert data["flow"] == {
        "empty": None,
        None: "blank-key",
        "explicit": None,
    }


def test_flow_sequence_pair_entries_are_single_pair_mappings():
    data = loads(
        dedent(
            """
            flow: [one: two, three: [four, five], ? [six, seven]: eight]
            """
        )
    )

    assert data["flow"] == [
        {"one": "two"},
        {"three": ["four", "five"]},
        {("six", "seven"): "eight"},
    ]


def test_flow_mapping_explicit_pair_entries():
    data = loads(
        dedent(
            """
            flow: {? [alpha, beta]: pair-key, ? explicit: value, plain: ok}
            """
        )
    )

    assert data["flow"] == {
        ("alpha", "beta"): "pair-key",
        "explicit": "value",
        "plain": "ok",
    }


def test_flow_mapping_explicit_key_without_value_resolves_to_null():
    data = loads(
        dedent(
            """
            flow: {? explicit, ? [alpha, beta]}
            """
        )
    )

    assert data["flow"] == {"explicit": None, ("alpha", "beta"): None}


def test_round_trip_emits_null_nodes_and_flow_pair_entries():
    doc = round_trip_loads(
        dedent(
            """
            empty:
            flow: [one: two, ? [three, four]: five]
            """
        )
    )

    dumped = round_trip_dumps(doc)

    assert "empty:" in dumped
    assert "flow: [{one: two}, {[three, four]: five}]" in dumped
    assert loads(dumped) == {
        "empty": None,
        "flow": [{"one": "two"}, {("three", "four"): "five"}],
    }
