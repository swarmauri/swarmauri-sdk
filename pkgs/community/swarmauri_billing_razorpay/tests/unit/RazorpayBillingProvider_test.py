import pytest
from swarmauri_billing_razorpay import RazorpayBillingProvider as Provider


@pytest.mark.unit
def test_ubc_resource():
    provider = Provider(
        api_key="razorpay-key",
        key_id="rzp_key",
        key_secret="rzp_secret",
    )
    assert provider.resource == "BillingProvider"


@pytest.mark.unit
def test_ubc_type():
    assert (
        Provider(
            api_key="razorpay-key",
            key_id="rzp_key",
            key_secret="rzp_secret",
        ).type
        == "RazorpayBillingProvider"
    )


@pytest.mark.unit
def test_initialization():
    provider = Provider(
        api_key="razorpay-key",
        key_id="rzp_key",
        key_secret="rzp_secret",
    )
    assert type(provider.id) is str


@pytest.mark.unit
def test_serialization():
    provider = Provider(
        api_key="razorpay-key",
        key_id="rzp_key",
        key_secret="rzp_secret",
    )
    assert provider.id == Provider.model_validate_json(provider.model_dump_json()).id
