from swarmauri_billing_mock import MockBillingProvider
from swarmauri_base.billing import ProductSpec

provider = MockBillingProvider(api_key="mock-key")
product = provider.create_product(
    ProductSpec(payload={"name": "Test"}),
    idempotency_key="mock-prod-1",
)

print(product.raw)
