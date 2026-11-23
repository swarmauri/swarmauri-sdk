from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

product = provider.create_product(
    ProductSpec(name="Analytics Plan", description="Advanced dashboards"),
    idempotency_key="razorpay-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="INR", unit_amount_minor=49900, nickname="Quarterly"),
    idempotency_key="razorpay-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/razorpay/callback",
        customer_email="buyer@example.com",
        idempotency_key="razorpay-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
