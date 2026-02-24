"""Lazy re-exports for :mod:`tigrbl_billing` operational helpers.

Each operation lives in its own module and is decorated with :func:`tigrbl.op_ctx`.
Importing an attribute from this package triggers loading of the minimal module that
defines it, ensuring operations are only registered when an API explicitly opts in
to them.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, Tuple

__all__ = [
    "apply_grant",
    "apply_top_off",
    "attach_payment_method",
    "cancel_payment_intent",
    "cancel_subscription",
    "capture_payment_intent",
    "charge_credits",
    "check_and_top_off",
    "create_or_link_customer",
    "finalize_invoice",
    "ingest_webhook_event",
    "mark_invoice_uncollectible",
    "pause_subscription",
    "proration_preview",
    "request_top_off",
    "resume_subscription",
    "refund_application_fee",
    "revoke_grant",
    "rollup_usage_periodic",
    "seat_assign",
    "seat_release",
    "seat_suspend",
    "start_subscription",
    "sync_objects",
    "trial_end",
    "trial_start",
    "void_invoice",
]

_LAZY_ATTRS: Dict[str, Tuple[str, str]] = {
    "apply_grant": ("grant_ops", "apply_grant"),
    "apply_top_off": ("balance_ops", "apply_top_off"),
    "attach_payment_method": ("customer_ops", "attach_payment_method"),
    "cancel_payment_intent": ("payment_ops", "cancel_payment_intent"),
    "cancel_subscription": ("subscription_ops", "cancel_subscription"),
    "capture_payment_intent": ("payment_ops", "capture_payment_intent"),
    "charge_credits": ("credit_usage_ops", "charge_credits"),
    "check_and_top_off": ("balance_ops", "check_and_top_off"),
    "create_or_link_customer": ("customer_ops", "create_or_link_customer"),
    "finalize_invoice": ("invoice_ops", "finalize_invoice"),
    "ingest_webhook_event": ("webhook_ops", "ingest_webhook_event"),
    "mark_invoice_uncollectible": ("invoice_ops", "mark_invoice_uncollectible"),
    "pause_subscription": ("subscription_ops", "pause_subscription"),
    "proration_preview": ("subscription_ops", "proration_preview"),
    "request_top_off": ("balance_ops", "request_top_off"),
    "resume_subscription": ("subscription_ops", "resume_subscription"),
    "refund_application_fee": ("connect_ops", "refund_application_fee"),
    "revoke_grant": ("grant_ops", "revoke_grant"),
    "rollup_usage_periodic": ("usage_ops", "rollup_usage_periodic"),
    "seat_assign": ("seats_ops", "seat_assign"),
    "seat_release": ("seats_ops", "seat_release"),
    "seat_suspend": ("seats_ops", "seat_suspend"),
    "start_subscription": ("subscription_ops", "start_subscription"),
    "sync_objects": ("sync_ops", "sync_objects"),
    "trial_end": ("subscription_ops", "trial_end"),
    "trial_start": ("subscription_ops", "trial_start"),
    "void_invoice": ("invoice_ops", "void_invoice"),
}


def __getattr__(name: str) -> Any:
    try:
        module_name, attr_name = _LAZY_ATTRS[name]
    except KeyError as exc:  # pragma: no cover - defensive programming
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    module = import_module(f"{__name__}.{module_name}")
    attr = getattr(module, attr_name)
    globals()[name] = attr
    return attr


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
