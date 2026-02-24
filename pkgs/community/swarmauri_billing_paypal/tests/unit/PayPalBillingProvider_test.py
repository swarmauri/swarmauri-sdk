import pytest
from swarmauri_billing_paypal import PayPalBillingProvider as Provider


@pytest.mark.unit
def test_ubc_resource():
    provider = Provider(api_key="paypal-key")
    assert provider.resource == "BillingProvider"


@pytest.mark.unit
def test_ubc_type():
    assert Provider(api_key="paypal-key").type == "PayPalBillingProvider"


@pytest.mark.unit
def test_initialization():
    provider = Provider(api_key="paypal-key")
    assert type(provider.id) is str


@pytest.mark.unit
def test_serialization():
    provider = Provider(api_key="paypal-key")
    assert provider.id == Provider.model_validate_json(provider.model_dump_json()).id
