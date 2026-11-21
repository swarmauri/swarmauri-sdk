from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

product = provider.create_product(
    ProductSpec(name="Learning Portal", description="Online academy access"),
    idempotency_key="paystack-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="NGN", unit_amount_minor=150000, nickname="Annual"),
    idempotency_key="paystack-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/paystack/callback",
        customer_email="learner@example.com",
        idempotency_key="paystack-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
