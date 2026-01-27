import pytest

from swarmauri_auth_idp_aws import AwsIdentityResolver


@pytest.fixture
def resolver() -> AwsIdentityResolver:
    return AwsIdentityResolver(
        region="us-east-1",
        sso_region="us-west-2",
        identity_store_id="d-123",
        account_id="123456789012",
        role_name="WorkforceReader",
    )


@pytest.mark.unit
def test_region_is_retained(resolver: AwsIdentityResolver) -> None:
    assert resolver.region == "us-east-1"


@pytest.mark.unit
def test_class_name(resolver: AwsIdentityResolver) -> None:
    assert resolver.__class__.__name__ == "AwsIdentityResolver"


@pytest.mark.unit
def test_initialization(resolver: AwsIdentityResolver) -> None:
    assert resolver.account_id == "123456789012"


@pytest.mark.unit
def test_lookup_user_min(
    monkeypatch: pytest.MonkeyPatch, resolver: AwsIdentityResolver
) -> None:
    class FakeResponse:
        def __init__(self) -> None:
            self._payload = {
                "roleCredentials": {
                    "accessKeyId": "ak",
                    "secretAccessKey": "sk",
                    "sessionToken": "st",
                }
            }

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self._payload

    class FakeIdentityStore:
        def list_users(self, IdentityStoreId: str, MaxResults: int):  # noqa: N803
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
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def client(self, name: str):
            assert name == "identitystore"
            return FakeIdentityStore()

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: FakeResponse())
    monkeypatch.setattr("boto3.Session", lambda **kwargs: FakeSession(**kwargs))

    result = resolver.lookup_user_min("access-token")
    assert result["userId"] == "u-1"
    assert result["emails"] == ["jane@example.com"]
