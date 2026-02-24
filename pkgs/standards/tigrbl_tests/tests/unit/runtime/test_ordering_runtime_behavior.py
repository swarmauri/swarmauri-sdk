from tigrbl.runtime import events as _ev
from tigrbl.runtime.labels import Label
from tigrbl.runtime.ordering import flatten


def test_flatten_orders_labels_by_runtime_anchor_sequence() -> None:
    labels = [
        Label(kind="atom", domain="wire", subject="build_out", anchor=_ev.OUT_BUILD),
        Label(
            kind="atom",
            domain="schema",
            subject="collect_in",
            anchor=_ev.SCHEMA_COLLECT_IN,
        ),
    ]

    ordered = flatten(labels, persist=True)

    assert [label.anchor for label in ordered] == [_ev.SCHEMA_COLLECT_IN, _ev.OUT_BUILD]


def test_flatten_prunes_persist_tied_anchors_when_non_persisting() -> None:
    labels = [
        Label(
            kind="atom",
            domain="resolve",
            subject="values",
            anchor=_ev.RESOLVE_VALUES,
        ),
        Label(kind="atom", domain="out", subject="build", anchor=_ev.OUT_BUILD),
    ]

    ordered = flatten(labels, persist=False)

    assert [label.anchor for label in ordered] == [_ev.OUT_BUILD]
