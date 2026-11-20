from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = StripeBillingProvider(api_key="sk_test_123")

product = provider.create_product(
    ProductSpec(name="Starter", description="Starter subscription"),
    idempotency_key="stripe-prod-001",
)
price = provider.create_price(
    product,
    PriceSpec(
        currency="USD", unit_amount_minor=1000, nickname="Starter monthly"
    ),
    idempotency_key="stripe-price-001",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        customer_email="buyer@example.com",
        idempotency_key="stripe-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
