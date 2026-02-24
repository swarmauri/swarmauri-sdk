import pytest
from swarmauri_billing_stripe import StripeBillingProvider as Provider


@pytest.mark.unit
def test_ubc_resource():
    provider = Provider(api_key="sk_test_123")
    assert provider.resource == "BillingProvider"


@pytest.mark.unit
def test_ubc_type():
    assert Provider(api_key="sk_test_123").type == "StripeBillingProvider"


@pytest.mark.unit
def test_initialization():
    provider = Provider(api_key="sk_test_123")
    assert type(provider.id) is str


@pytest.mark.unit
def test_serialization():
    provider = Provider(api_key="sk_test_123")
    assert provider.id == Provider.model_validate_json(provider.model_dump_json()).id
