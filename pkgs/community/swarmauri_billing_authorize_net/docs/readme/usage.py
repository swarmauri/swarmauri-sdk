from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider
from swarmauri_base.billing import PaymentIntentRequest, RefundRequest

provider = AuthorizeNetBillingProvider(
    api_key="authorize-net-transaction-key",
    login_id="authorize-net-login-id",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=4200,
        currency="USD",
        confirm=True,
        metadata={
            "opaque_data": {
                "dataDescriptor": "COMMON.ACCEPT.INAPP.PAYMENT",
                "dataValue": "opaque-payment-token",
            }
        },
    )
)
refund = provider.create_refund(
    payment,
    RefundRequest(amount_minor=4200),
    idempotency_key="refund-anet-1",
)

print(payment.status, refund["id"])
