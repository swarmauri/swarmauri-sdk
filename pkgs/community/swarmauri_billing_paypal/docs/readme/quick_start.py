from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PayPalBillingProvider(
    api_key="paypal",
    client_id="paypal-client-id",
    client_secret="paypal-client-secret",
)

product = provider.create_product(
    ProductSpec(name="Workspace"),
    idempotency_key="paypal-prod-1",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500),
    idempotency_key="paypal-price-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(success_url="https://example.com/return"),
)

print(product.id, price.id, checkout.url)
