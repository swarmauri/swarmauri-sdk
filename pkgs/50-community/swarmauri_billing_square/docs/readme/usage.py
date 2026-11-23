from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
    environment="sandbox",
)

product = provider.create_product(
    ProductSpec(name="Digital Membership", description="Premium access"),
    idempotency_key="prod-square-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500, nickname="Monthly"),
    idempotency_key="price-square-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/success",
        customer_email="buyer@example.com",
        idempotency_key="checkout-square-001",
    ),
)

print(product.id, price.id, checkout.url)
