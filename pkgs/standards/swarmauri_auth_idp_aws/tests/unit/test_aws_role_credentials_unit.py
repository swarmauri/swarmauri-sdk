"""Unit tests for temporary role credential validation (#6275).

``AwsIdentityResolver._get_role_credentials`` must validate the decoded
``roleCredentials`` object before a boto3 ``Session`` is created from it:
the response must carry non-empty string ``accessKeyId``,
``secretAccessKey``, and ``sessionToken`` values. Invalid responses fail
with a clear ``ValueError`` that never includes token or credential
values, and no boto3 ``Session`` is created.

Everything runs offline: the SSO federation endpoint and boto3 are
stubbed with fakes. No network access, credentials, or live AWS account
are needed.
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest

from swarmauri_auth_idp_aws import AwsIdentityResolver

VALID_CREDENTIALS = {
    "accessKeyId": "AKIA-VALID-KEY",
    "secretAccessKey": "valid-secret",
    "sessionToken": "valid-token",
}


@pytest.fixture
def resolver() -> AwsIdentityResolver:
    return AwsIdentityResolver(
        region="us-east-1",
        sso_region="us-west-2",
        identity_store_id="d-123",
        account_id="123456789012",
        role_name="WorkforceReader",
    )


class FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


class FakeIdentityStore:
    def list_users(self, IdentityStoreId: str, MaxResults: int):
        assert IdentityStoreId == "d-123"
        return {
            "Users": [
                {
                    "UserId": "u-1",
                    "UserName": "jdoe",
                    "DisplayName": "Jane Doe",
                    "Emails": [{"Value": "jane@example.com"}],
                }
            ]
        }


class FakeSession:
    calls: ClassVar[list[dict[str, Any]]] = []

    def __init__(self, **kwargs: Any) -> None:
        FakeSession.calls.append(kwargs)

    def client(self, name: str) -> FakeIdentityStore:
        assert name == "identitystore"
        return FakeIdentityStore()


@pytest.fixture
def stubbed_aws(monkeypatch: pytest.MonkeyPatch):
    FakeSession.calls = []

    def install(payload: Any) -> None:
        monkeypatch.setattr("httpx.get", lambda *args, **kwargs: FakeResponse(payload))
        monkeypatch.setattr("boto3.Session", FakeSession)

    return install


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    credentials = dict(VALID_CREDENTIALS)
    credentials.update(overrides)
    return {"roleCredentials": credentials}


@pytest.mark.unit
def test_valid_credentials_reach_boto3(
    stubbed_aws, resolver: AwsIdentityResolver
) -> None:
    stubbed_aws(_valid_payload())
    result = resolver.lookup_user_min("access-token")
    assert result["userId"] == "u-1"
    assert result["emails"] == ["jane@example.com"]
    assert len(FakeSession.calls) == 1
    assert FakeSession.calls[0] == {
        "aws_access_key_id": "AKIA-VALID-KEY",
        "aws_secret_access_key": "valid-secret",
        "aws_session_token": "valid-token",
        "region_name": "us-east-1",
    }


@pytest.mark.unit
@pytest.mark.parametrize("payload", [{}, {"other": {}}, {"roleCredentials": None}])
def test_missing_or_null_role_credentials(
    stubbed_aws, resolver: AwsIdentityResolver, payload: dict[str, Any]
) -> None:
    stubbed_aws(payload)
    with pytest.raises(ValueError, match="missing roleCredentials"):
        resolver.lookup_user_min("access-token")
    assert FakeSession.calls == []


@pytest.mark.unit
@pytest.mark.parametrize("credentials", ["not-a-mapping", ["ak", "sk", "st"], 42])
def test_non_mapping_role_credentials(
    stubbed_aws, resolver: AwsIdentityResolver, credentials: Any
) -> None:
    stubbed_aws({"roleCredentials": credentials})
    with pytest.raises(ValueError, match="missing roleCredentials"):
        resolver.lookup_user_min("access-token")
    assert FakeSession.calls == []


@pytest.mark.unit
@pytest.mark.parametrize("field", ["accessKeyId", "secretAccessKey", "sessionToken"])
@pytest.mark.parametrize("bad_value", [None, "", 123, ["x"]])
def test_missing_empty_or_non_string_field(
    stubbed_aws,
    resolver: AwsIdentityResolver,
    field: str,
    bad_value: Any,
) -> None:
    payload = _valid_payload()
    if bad_value is None:
        del payload["roleCredentials"][field]
    else:
        payload["roleCredentials"][field] = bad_value
    stubbed_aws(payload)
    with pytest.raises(ValueError, match=f"missing or empty {field}"):
        resolver.lookup_user_min("access-token")
    assert FakeSession.calls == []


@pytest.mark.unit
def test_error_contains_no_credential_values(
    stubbed_aws, resolver: AwsIdentityResolver
) -> None:
    payload = _valid_payload()
    del payload["roleCredentials"]["sessionToken"]
    stubbed_aws(payload)
    with pytest.raises(ValueError) as excinfo:
        resolver.lookup_user_min("access-token")
    message = str(excinfo.value)
    assert "AKIA-VALID-KEY" not in message
    assert "valid-secret" not in message
    assert "valid-token" not in message
    assert "access-token" not in message
    assert FakeSession.calls == []
