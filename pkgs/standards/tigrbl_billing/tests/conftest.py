import sys
import types
import uuid
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

import pytest

PACKAGE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PACKAGE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ----------------------------------------------------------------------------
# Minimal tigrbl stubs (decorator + typing aliases)
# ----------------------------------------------------------------------------


def _op_ctx_decorator(**metadata):
    def decorator(func):
        setattr(func, "_tigrbl_ctx", metadata)
        return func

    return decorator


tigrbl_module = types.ModuleType("tigrbl")
tigrbl_module.op_ctx = _op_ctx_decorator
sys.modules.setdefault("tigrbl", tigrbl_module)

tigrbl_types_module = types.ModuleType("tigrbl.types")
tigrbl_types_module.Session = object
tigrbl_types_module.UUID = str
sys.modules.setdefault("tigrbl.types", tigrbl_types_module)


# ----------------------------------------------------------------------------
# In-memory ORM primitives used by the ops during testing
# ----------------------------------------------------------------------------


class ComparableColumn:
    def __init__(self, name: str):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def _predicate(
        self, comparator: Callable[[Any, Any], bool], other: Any
    ) -> Callable[[Any], bool]:
        return lambda obj: comparator(getattr(obj, self.name, None), other)

    def __eq__(self, other: Any) -> Callable[[Any], bool]:
        return self._predicate(lambda a, b: a == b, other)

    def __ge__(self, other: Any) -> Callable[[Any], bool]:
        return self._predicate(lambda a, b: a >= b, other)

    def __lt__(self, other: Any) -> Callable[[Any], bool]:
        return self._predicate(lambda a, b: a < b, other)


class _Query:
    def __init__(self, model_cls: type):
        self._model_cls = model_cls
        self._predicates: List[Callable[[Any], bool]] = []

    def filter(self, *predicates: Iterable[Callable[[Any], bool]]):
        for predicate in predicates:
            if predicate is None:
                continue
            if not callable(predicate):
                raise TypeError("predicates must be callables in stub query")
            self._predicates.append(predicate)
        return self

    def _apply(self) -> List[Any]:
        data = list(self._model_cls._storage)  # type: ignore[attr-defined]
        for predicate in self._predicates:
            data = [obj for obj in data if predicate(obj)]
        return data

    def one_or_none(self):
        data = self._apply()
        if not data:
            return None
        if len(data) > 1:
            raise ValueError("multiple results in stub query")
        return data[0]

    def all(self):
        return self._apply()


class _Session:
    def __init__(self, model_cls: type):
        self._model_cls = model_cls

    def query(self, model_cls: type) -> _Query:
        return _Query(model_cls)

    def add(self, obj: Any):
        storage = obj.__class__._storage  # type: ignore[attr-defined]
        if obj not in storage:
            storage.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None


class StubModel:
    id = ComparableColumn("id")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._storage: List[Any] = []

    def __init__(self, **fields: Any):
        self.id = fields.pop("id", str(uuid.uuid4()))
        for key, value in fields.items():
            setattr(self, key, value)

    @classmethod
    def acquire(cls, op_alias: str | None = None):
        return _Session(cls), lambda: None

    @classmethod
    def reset(cls):
        cls._storage.clear()


_REGISTERED_MODELS: List[type] = []


def make_model(name: str, columns: Iterable[str]):
    attrs: Dict[str, ComparableColumn] = {col: ComparableColumn(col) for col in columns}
    model_cls = type(name, (StubModel,), attrs)
    _REGISTERED_MODELS.append(model_cls)
    return model_cls


# ----------------------------------------------------------------------------
# Stub table modules
tables_pkg = types.ModuleType("tigrbl_billing.tables")
tables_pkg.__path__ = []  # treat as namespace package
sys.modules.setdefault("tigrbl_billing.tables", tables_pkg)


def _register_module(module_name: str, **attrs: Any):
    module = types.ModuleType(module_name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[module_name] = module
    parent_name = module_name.rsplit(".", 1)[0]
    parent = sys.modules.get(parent_name)
    if parent is not None:
        setattr(parent, module_name.split(".")[-1], module)
    return module


# Enumerations mirroring production names
TopOffTrigger = Enum(
    "TopOffTrigger", {"MANUAL": "manual", "AUTO": "auto", "SYSTEM": "system"}
)
TopOffMethod = Enum(
    "TopOffMethod",
    {
        "PAYMENT_INTENT": "payment_intent",
        "EXTERNAL_TRANSFER": "external_transfer",
        "GRANT": "grant",
    },
)
TopOffStatus = Enum(
    "TopOffStatus",
    {"INITIATED": "initiated", "SUCCEEDED": "succeeded", "FAILED": "failed"},
)
LedgerDirection = Enum("LedgerDirection", {"DEBIT": "debit", "CREDIT": "credit"})
GrantStatus = Enum(
    "GrantStatus", {"ACTIVE": "active", "REVOKED": "revoked", "EXPIRED": "expired"}
)
InvoiceStatus = Enum(
    "InvoiceStatus",
    {"OPEN": "open", "VOID": "void", "UNCOLLECTIBLE": "uncollectible"},
)
PaymentIntentStatus = Enum(
    "PaymentIntentStatus",
    {
        "SUCCEEDED": "succeeded",
        "CANCELED": "canceled",
        "REQUIRES_CAPTURE": "requires_capture",
    },
)
SeatState = Enum(
    "SeatState", {"ACTIVE": "active", "SUSPENDED": "suspended", "RELEASED": "released"}
)
SubscriptionStatus = Enum(
    "SubscriptionStatus",
    {
        "TRIALING": "trialing",
        "ACTIVE": "active",
        "PAST_DUE": "past_due",
        "CANCELED": "canceled",
    },
)
EventProcessStatus = Enum(
    "EventProcessStatus", {"RECEIVED": "received", "PROCESSED": "processed"}
)

# Model definitions used by ops
BalanceTopOff = make_model(
    "BalanceTopOff", ["status", "metadata", "processed_at", "failure_reason"]
)
CustomerBalance = make_model("CustomerBalance", ["balance_id"])
ApplicationFee = make_model("ApplicationFee", ["stripe_application_fee_id", "refunded"])
UsageEvent = make_model(
    "UsageEvent",
    [
        "usage_event_id",
        "customer_id",
        "feature_key",
        "quantity",
        "currency",
        "metadata",
        "event_ts",
        "subscription_item_id",
    ],
)
CreditGrant = make_model("CreditGrant", ["status", "revoke_amount", "revoke_reason"])
Invoice = make_model("Invoice", ["status", "line_items"])
PaymentIntent = make_model("PaymentIntent", ["status"])
SeatAllocation = make_model(
    "SeatAllocation", ["state", "subscription_item_id", "subject_ref", "role"]
)
Subscription = make_model(
    "Subscription",
    [
        "customer_id",
        "status",
        "cancel_at_period_end",
        "current_period_start",
        "current_period_end",
        "trial_end",
        "collection_method",
        "days_until_due",
        "stripe_subscription_id",
        "metadata",
        "items",
    ],
)
UsageRollup = make_model(
    "UsageRollup",
    [
        "subscription_item_id",
        "period_start",
        "period_end",
        "quantity_sum",
        "last_event_ts",
    ],
)
StripeEventLog = make_model(
    "StripeEventLog",
    [
        "stripe_event_id",
        "event_type",
        "api_version",
        "event_created_ts",
        "account",
        "payload",
        "status",
        "processed_at",
        "error_message",
        "stripe_request_id",
    ],
)
Product = make_model(
    "Product", ["stripe_product_id", "name", "description", "metadata"]
)
Price = make_model("Price", ["stripe_price_id", "unit_amount"])
PriceTier = make_model("PriceTier", ["price_id", "up_to", "unit_amount"])
Customer = make_model(
    "Customer",
    [
        "email",
        "name",
        "stripe_customer_id",
        "default_payment_method_ref",
        "tax_exempt",
        "metadata",
        "active",
    ],
)
SubscriptionItem = make_model(
    "SubscriptionItem",
    ["subscription_id", "stripe_subscription_item_id", "quantity", "price_id"],
)
InvoiceLineItem = make_model(
    "InvoiceLineItem",
    ["invoice_id", "stripe_invoice_line_item_id", "amount", "description"],
)
Refund = make_model("Refund", ["stripe_refund_id", "amount"])
ConnectedAccount = make_model(
    "ConnectedAccount", ["stripe_account_id", "details_submitted"]
)
Transfer = make_model("Transfer", ["stripe_transfer_id", "amount", "currency"])

_register_module(
    "tigrbl_billing.tables.balance_top_off",
    BalanceTopOff=BalanceTopOff,
    TopOffTrigger=TopOffTrigger,
    TopOffMethod=TopOffMethod,
    TopOffStatus=TopOffStatus,
)
_register_module(
    "tigrbl_billing.tables.customer_balance", CustomerBalance=CustomerBalance
)
_register_module("tigrbl_billing.tables.application_fee", ApplicationFee=ApplicationFee)
_register_module("tigrbl_billing.tables.credit_ledger", LedgerDirection=LedgerDirection)
_register_module("tigrbl_billing.tables.usage_event", UsageEvent=UsageEvent)
_register_module(
    "tigrbl_billing.tables.credit_grant",
    CreditGrant=CreditGrant,
    GrantStatus=GrantStatus,
)
_register_module(
    "tigrbl_billing.tables.invoice",
    Invoice=Invoice,
    InvoiceStatus=InvoiceStatus,
)
_register_module(
    "tigrbl_billing.tables.payment_intent",
    PaymentIntent=PaymentIntent,
    PaymentIntentStatus=PaymentIntentStatus,
)
_register_module(
    "tigrbl_billing.tables.seat_allocation",
    SeatAllocation=SeatAllocation,
    SeatState=SeatState,
)
_register_module(
    "tigrbl_billing.tables.subscription",
    Subscription=Subscription,
    SubscriptionStatus=SubscriptionStatus,
)
_register_module(
    "tigrbl_billing.tables.subscription_item", SubscriptionItem=SubscriptionItem
)
_register_module("tigrbl_billing.tables.product", Product=Product)
_register_module("tigrbl_billing.tables.price", Price=Price)
_register_module("tigrbl_billing.tables.price_tier", PriceTier=PriceTier)
_register_module("tigrbl_billing.tables.customer", Customer=Customer)
_register_module(
    "tigrbl_billing.tables.invoice_line_item", InvoiceLineItem=InvoiceLineItem
)
_register_module("tigrbl_billing.tables.refund", Refund=Refund)
_register_module(
    "tigrbl_billing.tables.connected_account", ConnectedAccount=ConnectedAccount
)
_register_module("tigrbl_billing.tables.transfer", Transfer=Transfer)
_register_module(
    "tigrbl_billing.tables.usage_rollup",
    UsageRollup=UsageRollup,
)
_register_module(
    "tigrbl_billing.tables.stripe_event_log",
    StripeEventLog=StripeEventLog,
    EventProcessStatus=EventProcessStatus,
)


# ----------------------------------------------------------------------------
# Shared helpers for tests
# ----------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_stub_models():
    for model_cls in _REGISTERED_MODELS:
        model_cls.reset()


class RecordingHandler:
    def __init__(self, result: Any = None):
        self.result = result if result is not None else {"ok": True}
        self.calls: List[Dict[str, Any]] = []

    async def handler(self, ctx: Dict[str, Any]):
        self.calls.append({**ctx})
        return self.result


class RecordingModel:
    def __init__(self, result: Any = None):
        self.handlers = types.SimpleNamespace(
            create=RecordingHandler(result),
            update=RecordingHandler(result),
            merge=RecordingHandler(result),
        )


@pytest.fixture
def recording_model():
    return RecordingModel(result={"status": "ok"})


@pytest.fixture
def blank_ctx():
    return {}
