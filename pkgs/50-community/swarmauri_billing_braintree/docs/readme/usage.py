from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = BraintreeBillingProvider(
    api_key="braintree",
    merchant_id="merchant-id",
    public_key="public-key",
    private_key="private-key",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=1500,
        currency="USD",
        confirm=True,
    )
)
captured = provider.capture_payment(payment.id, idempotency_key="capture-bt-1")

print(payment.status, captured.status)
