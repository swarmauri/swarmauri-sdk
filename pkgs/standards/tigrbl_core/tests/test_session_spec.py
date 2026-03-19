from __future__ import annotations

import pytest

from tigrbl_core._spec.session_spec import (
    SessionSpec,
    readonly,
    session_spec,
    tx_read_committed,
    tx_repeatable_read,
    tx_serializable,
)


def test_from_any_supports_aliases_and_filters_unknown_fields() -> None:
    spec = SessionSpec.from_any({"iso": "serializable", "readonly": True, "x": 1})

    assert spec is not None
    assert spec.isolation == "serializable"
    assert spec.read_only is True


def test_merge_prefers_non_none_from_higher() -> None:
    base = SessionSpec(isolation="read_committed", read_only=False)
    merged = base.merge({"read_only": True, "max_retries": 2})

    assert merged.isolation == "read_committed"
    assert merged.read_only is True
    assert merged.max_retries == 2


def test_session_helpers_and_validation() -> None:
    assert tx_read_committed(read_only=True).isolation == "read_committed"
    assert tx_repeatable_read().isolation == "repeatable_read"
    assert tx_serializable().isolation == "serializable"
    assert readonly().read_only is True
    assert session_spec(max_retries=3).max_retries == 3

    with pytest.raises(ValueError, match="either a mapping/spec or kwargs"):
        session_spec({"read_only": True}, max_retries=1)
