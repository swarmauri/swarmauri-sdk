import datetime as dt
from types import SimpleNamespace

from tigrbl_api_hpks.ops import pks


def _build_key(**overrides):
    defaults = {
        "is_revoked": NotImplemented,
        "revocation_date": None,
        "revocation_signatures": [],
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_extract_revocation_state_treats_unknown_flags_as_active():
    revoked, revoked_at = pks._extract_revocation_state(_build_key())
    assert revoked is False
    assert revoked_at is None


def test_extract_revocation_state_prefers_revocation_date():
    timestamp = dt.datetime.now(dt.timezone.utc)
    revoked, revoked_at = pks._extract_revocation_state(
        _build_key(is_revoked=False, revocation_date=timestamp)
    )
    assert revoked is True
    assert revoked_at == timestamp


def test_extract_revocation_state_uses_signature_metadata():
    created = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)
    signature = SimpleNamespace(created=created)
    revoked, revoked_at = pks._extract_revocation_state(
        _build_key(revocation_signatures=[signature])
    )
    assert revoked is True
    assert revoked_at == created
