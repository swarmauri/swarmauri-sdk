import pytest
from swarmauri_billing_braintree import BraintreeBillingProvider as Provider


@pytest.mark.unit
def test_ubc_resource():
    provider = Provider(api_key="braintree-key")
    assert provider.resource == "BillingProvider"


@pytest.mark.unit
def test_ubc_type():
    assert Provider(api_key="braintree-key").type == "BraintreeBillingProvider"


@pytest.mark.unit
def test_initialization():
    provider = Provider(api_key="braintree-key")
    assert type(provider.id) is str


@pytest.mark.unit
def test_serialization():
    provider = Provider(api_key="braintree-key")
    assert provider.id == Provider.model_validate_json(provider.model_dump_json()).id
