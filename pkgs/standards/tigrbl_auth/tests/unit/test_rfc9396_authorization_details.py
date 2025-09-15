"""Tests for RFC 9396 Rich Authorization Requests.

Excerpt from RFC 9396 §2:

    The request parameter authorization_details contains, in JSON notation,
    an array of objects. Each JSON object contains the data to specify the
    authorization requirements for a certain type of resource. The type
    field is REQUIRED.

These tests ensure that our parser follows the above requirements and can be
conditionally enabled or disabled via runtime configuration.
"""

import pytest

from tigrbl_auth.rfc.rfc9396 import (
    AuthorizationDetail,
    RFC9396_SPEC_URL,
    parse_authorization_details,
)
from tigrbl_auth.runtime_cfg import settings


def test_parse_authorization_details_enabled(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc9396", True)
    details = parse_authorization_details(
        '{"type": "payment_initiation", "actions": ["initiate"]}'
    )
    assert isinstance(details[0], AuthorizationDetail)
    assert details[0].type == "payment_initiation"


def test_parse_authorization_details_missing_type(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc9396", True)
    with pytest.raises(ValueError):
        parse_authorization_details('{"actions": ["initiate"]}')


def test_parse_authorization_details_disabled(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc9396", False)
    with pytest.raises(NotImplementedError):
        parse_authorization_details('{"type": "payment_initiation"}')


def test_parse_authorization_details_list(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc9396", True)
    raw = '[{"type": "a"}, {"type": "b"}]'
    details = parse_authorization_details(raw)
    assert [d.type for d in details] == ["a", "b"]


def test_parse_authorization_details_invalid_json(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc9396", True)
    with pytest.raises(ValueError):
        parse_authorization_details("not-json")


def test_parse_authorization_details_wrong_type(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc9396", True)
    with pytest.raises(ValueError):
        parse_authorization_details("123")


def test_rfc9396_spec_url():
    assert RFC9396_SPEC_URL.endswith("rfc9396")
