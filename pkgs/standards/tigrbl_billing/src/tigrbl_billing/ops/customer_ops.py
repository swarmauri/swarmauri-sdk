from __future__ import annotations
from typing import Optional
from tigrbl import op_ctx

from tigrbl_billing.tables.customer import Customer


@op_ctx(
    alias="create_or_link_customer",
    target="custom",
    arity="collection",
    bind=Customer,
    persist="default",
)
async def create_or_link_customer(
    *,
    email: Optional[str] = None,
    name: Optional[str] = None,
    stripe_customer_id: Optional[str] = None,
    default_payment_method_ref: Optional[str] = None,
    tax_exempt: str = "none",
    metadata: Optional[dict] = None,
    active: bool = True,
    model=None,
    ctx=None,
    payload=None,
    spec=None,
) -> dict:
    """Upsert-like behavior via the model's bound handlers.
    We do NOT touch DB or sessions directly.
    Strategy:
      - prefer merge() so unique keys on model handle linkage (e.g., stripe_customer_id or email)
      - payload only; no *_ctx in signature
    """
    te = (tax_exempt or "none").upper()
    te_enum = te if te in {"NONE", "EXEMPT", "REVERSE"} else "NONE"
    ctx["payload"] = {
        "email": email,
        "name": name,
        "stripe_customer_id": stripe_customer_id,
        "default_payment_method_ref": default_payment_method_ref,
        "tax_exempt": te_enum,
        "metadata": metadata or {},
        "active": bool(active),
    }
    # Delegate to the model's bounded merge handler (upsert semantics).
    return await model.handlers.merge.handler(ctx)


@op_ctx(
    alias="attach_payment_method",
    target="custom",
    arity="member",
    bind=Customer,
    persist="default",
)
async def attach_payment_method(
    *,
    customer_id,
    payment_method_ref: str,
    model=None,
    ctx=None,
    payload=None,
    spec=None,
) -> dict:
    # set PK path param + payload for update
    ctx["path_params"] = {"customer_id": customer_id}
    ctx["payload"] = {"default_payment_method_ref": payment_method_ref}
    return await model.handlers.update.handler(ctx)
