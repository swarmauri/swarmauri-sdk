from tigrbl.runtime import events as _ev


def test_order_events_returns_canonical_runtime_sequence() -> None:
    anchors = [_ev.OUT_DUMP, _ev.DEP_SECURITY, _ev.OUT_BUILD]

    assert _ev.order_events(anchors) == [_ev.DEP_SECURITY, _ev.OUT_BUILD, _ev.OUT_DUMP]


def test_prune_events_for_persist_keeps_non_persist_tied_only() -> None:
    anchors = [_ev.RESOLVE_VALUES, _ev.SCHEMA_COLLECT_IN, _ev.OUT_DUMP]

    assert _ev.prune_events_for_persist(anchors, persist=False) == [
        _ev.SCHEMA_COLLECT_IN,
        _ev.OUT_DUMP,
    ]


def test_phases_follow_expected_kernel_execution_order() -> None:
    assert _ev.PHASES[:9] == (
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "END_TX",
        "POST_COMMIT",
        "POST_RESPONSE",
    )
