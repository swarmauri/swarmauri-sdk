from types import SimpleNamespace

from tigrbl_billing.ops import sync_ops
from tigrbl_billing.tables.product import Product
from tigrbl_billing.tables.price import Price


def test_sync_objects_inserts_records():
    op_ctx = SimpleNamespace(alias="sync")

    result = sync_ops.sync_objects(
        op_ctx,
        engine_ctx=None,
        schema_ctx=None,
        products=[
            {
                "stripe_product_id": "prod_1",
                "name": "Product",
                "description": "Desc",
                "metadata": {},
            }
        ],
        prices=[{"stripe_price_id": "price_1", "unit_amount": 1000}],
    )

    assert result == {"products": 1, "prices": 1}
    stored_product = Product._storage[0]
    assert stored_product.stripe_product_id == "prod_1"
    assert stored_product.name == "Product"
    stored_price = Price._storage[0]
    assert stored_price.stripe_price_id == "price_1"
    assert stored_price.unit_amount == 1000


def test_sync_objects_updates_existing_records():
    op_ctx = SimpleNamespace(alias="sync")
    existing = Product(
        stripe_product_id="prod_2", name="Old", description="Old", metadata={}
    )
    Product._storage.append(existing)

    result = sync_ops.sync_objects(
        op_ctx,
        engine_ctx=None,
        schema_ctx=None,
        products=[
            {"stripe_product_id": "prod_2", "name": "New", "description": "Newer"}
        ],
    )

    assert result == {"products": 1}
    assert Product._storage[0] is existing
    assert existing.name == "New"
    assert existing.description == "Newer"
