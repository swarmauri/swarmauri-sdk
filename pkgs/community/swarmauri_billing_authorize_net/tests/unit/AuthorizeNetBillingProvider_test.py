import pytest
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider as Provider


@pytest.mark.unit
def test_ubc_resource():
    provider = Provider(api_key="authorize-net-key")
    assert provider.resource == "BillingProvider"


@pytest.mark.unit
def test_ubc_type():
    assert Provider(api_key="authorize-net-key").type == "AuthorizeNetBillingProvider"


@pytest.mark.unit
def test_initialization():
    provider = Provider(api_key="authorize-net-key")
    assert type(provider.id) is str


@pytest.mark.unit
def test_serialization():
    provider = Provider(api_key="authorize-net-key")
    assert provider.id == Provider.model_validate_json(provider.model_dump_json()).id
