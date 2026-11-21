from swarmauri_billing_adyen import AdyenBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = AdyenBillingProvider(
    api_key="adyen-test-key",
    merchant_account="YourMerchantAccount",
)

product = provider.create_product(
    ProductSpec(name="Enterprise Plan"),
    idempotency_key="prod-ady-1",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=49900),
    idempotency_key="price-ady-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(success_url="https://merchant.example/success"),
)

print(product.id, price.id, checkout.id)
