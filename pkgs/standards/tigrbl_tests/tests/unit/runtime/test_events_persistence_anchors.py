from tigrbl.runtime import events as _ev
from tigrbl.runtime import system as _sys


def test_persistence_system_anchors_are_canonical_events() -> None:
    assert _ev.is_valid_event(_ev.SYS_TXN_BEGIN)
    assert _ev.is_valid_event(_ev.SYS_HANDLER_CRUD)
    assert _ev.is_valid_event(_ev.SYS_TXN_COMMIT)


def test_persistence_system_anchors_have_expected_phases() -> None:
    assert _ev.phase_for_event(_ev.SYS_TXN_BEGIN) == "START_TX"
    assert _ev.phase_for_event(_ev.SYS_HANDLER_CRUD) == "HANDLER"
    assert _ev.phase_for_event(_ev.SYS_TXN_COMMIT) == "END_TX"


def test_system_registry_points_to_canonical_persistence_events() -> None:
    assert _sys.get("txn", "begin")[0] == _ev.SYS_TXN_BEGIN
    assert _sys.get("handler", "crud")[0] == _ev.SYS_HANDLER_CRUD
    assert _sys.get("txn", "commit")[0] == _ev.SYS_TXN_COMMIT


def test_order_events_places_system_persistence_between_pre_and_post_handler() -> None:
    ordered = _ev.order_events(
        [_ev.OUT_BUILD, _ev.SYS_TXN_COMMIT, _ev.SYS_HANDLER_CRUD, _ev.SYS_TXN_BEGIN]
    )
    assert ordered == [
        _ev.SYS_TXN_BEGIN,
        _ev.SYS_HANDLER_CRUD,
        _ev.SYS_TXN_COMMIT,
        _ev.OUT_BUILD,
    ]
