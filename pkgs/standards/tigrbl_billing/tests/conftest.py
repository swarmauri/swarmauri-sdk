import asyncio
import contextlib
import inspect
import functools
import re
import socket
import sys
import threading
import types
import uuid
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence

import httpx
import pytest
import uvicorn
from fastapi import APIRouter, Body, FastAPI, HTTPException

PACKAGE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PACKAGE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ----------------------------------------------------------------------------
# Minimal tigrbl stubs (decorator + typing aliases)
# ----------------------------------------------------------------------------

_REGISTERED_API_OPS: Dict[type, List[Dict[str, Any]]] = {}


def _op_ctx_decorator(**metadata):
    def decorator(func):
        meta = dict(metadata)
        setattr(func, "_tigrbl_ctx", meta)
        bind = meta.get("bind")
        module_name = func.__module__ or ""
        is_api_wrapper = ".api." in module_name
        if bind is not None and isinstance(bind, type) and is_api_wrapper:
            ops = _REGISTERED_API_OPS.setdefault(bind, [])
            alias = meta.get("alias")
            if alias and not any(
                entry["alias"] == alias and entry["module"] == func.__module__
                for entry in ops
            ):
                ops.append(
                    {
                        "alias": alias,
                        "func": func,
                        "module": func.__module__,
                    }
                )
        if is_api_wrapper:
            return func

        # Adapter for ops-layer functions so they behave like their decorated counterparts.
        is_async = inspect.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_adapter(
                ctx=None, engine_ctx=None, schema_ctx=None, **payload
            ):
                payload = dict(payload)
                actual_ctx = ctx if isinstance(ctx, dict) else payload.pop("ctx", None)
                if actual_ctx is None:
                    actual_ctx = {}
                model = payload.pop("model", None) or bind
                result = await func(model=model, ctx=actual_ctx, **payload)
                return result

            return async_adapter

        @functools.wraps(func)
        def adapter(ctx=None, engine_ctx=None, schema_ctx=None, **payload):
            payload = dict(payload)
            actual_ctx = ctx if isinstance(ctx, dict) else payload.pop("ctx", None)
            if actual_ctx is None:
                actual_ctx = {}
            model = payload.pop("model", None) or bind
            return func(model=model, ctx=actual_ctx, **payload)

        return adapter

    return decorator


tigrbl_module = types.ModuleType("tigrbl")
tigrbl_module.op_ctx = _op_ctx_decorator
sys.modules.setdefault("tigrbl", tigrbl_module)

tigrbl_engine_module = types.ModuleType("tigrbl.engine")
tigrbl_engine_shortcuts = types.ModuleType("tigrbl.engine.shortcuts")
sys.modules.setdefault("tigrbl.engine", tigrbl_engine_module)
sys.modules.setdefault("tigrbl.engine.shortcuts", tigrbl_engine_shortcuts)
tigrbl_engine_module.shortcuts = tigrbl_engine_shortcuts  # type: ignore[attr-defined]


def _stub_build_engine(cfg: Mapping[str, Any] | None = None, **_) -> Mapping[str, Any]:
    return dict(cfg or {})


def _stub_mem(async_: bool = True) -> Mapping[str, Any]:
    return {"kind": "sqlite", "async": bool(async_)}


tigrbl_engine_shortcuts.engine = _stub_build_engine  # type: ignore[attr-defined]
tigrbl_engine_shortcuts.mem = _stub_mem  # type: ignore[attr-defined]

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


def _resource_name(model: type) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", model.__name__).lower()


def _serialize_instance(obj: Any) -> Dict[str, Any]:
    return {k: v for k, v in vars(obj).items() if not k.startswith("_")}


def _ensure_model_handlers(model: type) -> None:
    if getattr(model, "handlers", None) is not None:
        return

    storage: List[Any] = getattr(model, "_storage", None)
    if storage is None:
        storage = []
        setattr(model, "_storage", storage)

    resource = _resource_name(model)
    alias_field = f"{resource}_id"

    def _resolve_identifier(
        ctx: Mapping[str, Any] | None, payload: Mapping[str, Any]
    ) -> tuple[Any | None, set[str]]:
        identifier: Any | None = None
        keys: set[str] = set()
        ctx_map: Mapping[str, Any] = ctx or {}
        path_params = ctx_map.get("path_params") or {}
        if isinstance(path_params, Mapping):
            for key, value in path_params.items():
                keys.add(key)
                if identifier is None and value is not None:
                    identifier = value
        for key in ("id", alias_field):
            if identifier is not None:
                break
            value = payload.get(key)
            if value is not None:
                identifier = value
                keys.add(key)
        if identifier is None:
            for key, value in payload.items():
                if key.endswith("_id") and value is not None:
                    identifier = value
                    keys.add(key)
                    break
        return identifier, keys

    def _candidate_keys(keys: Iterable[str], payload: Mapping[str, Any]) -> set[str]:
        candidates = {"id", alias_field}
        candidates.update(keys)
        candidates.update(
            {k for k, v in payload.items() if k.endswith("_id") and v is not None}
        )
        candidates.update({k for k in ("external_id", "email") if k in payload})
        return candidates

    def _find_by_identifier(
        identifier: Any | None, keys: Iterable[str], payload: Mapping[str, Any]
    ) -> Any | None:
        if identifier is None:
            return None
        candidates = _candidate_keys(keys, payload)
        for obj in storage:
            for key in candidates:
                if getattr(obj, key, None) == identifier:
                    return obj
        return None

    def _find_by_payload(payload: Mapping[str, Any]) -> Any | None:
        if not payload:
            return None
        priority_keys = [
            key
            for key in payload
            if key.endswith("_id") or key in {"external_id", "email"}
        ]
        for obj in storage:
            if any(
                payload.get(key) is not None
                and getattr(obj, key, None) == payload.get(key)
                for key in priority_keys
            ):
                return obj
        return None

    class _Handler:
        def __init__(self, action: str):
            self.action = action
            self.calls: List[Dict[str, Any]] = []

        async def handler(self, ctx: Mapping[str, Any] | None):
            ctx_map: Dict[str, Any] = dict(ctx or {})
            payload: Dict[str, Any] = dict(ctx_map.get("payload") or {})
            path_params: Dict[str, Any] = dict(ctx_map.get("path_params") or {})
            self.calls.append(
                {"payload": payload.copy(), "path_params": path_params.copy()}
            )

            if self.action == "create":
                obj = model(**payload)
                if not getattr(obj, alias_field, None):
                    setattr(obj, alias_field, getattr(obj, "id", None))
                for key, value in payload.items():
                    if key.endswith("_id") and value is not None:
                        setattr(obj, key, value)
                storage.append(obj)
                return {"status": "ok", "data": _serialize_instance(obj)}

            if self.action == "list":
                return {"items": [_serialize_instance(obj) for obj in storage]}

            if self.action == "read":
                identifier, keys = _resolve_identifier(ctx_map, payload)
                target = _find_by_identifier(identifier, keys, payload)
                if target is None:
                    raise HTTPException(status_code=404, detail="Item not found")
                return _serialize_instance(target)

            if self.action in {"update", "replace"}:
                identifier, keys = _resolve_identifier(ctx_map, payload)
                target = _find_by_identifier(identifier, keys, payload)
                if target is None:
                    raise HTTPException(status_code=404, detail="Item not found")
                for key, value in payload.items():
                    setattr(target, key, value)
                return {"status": "ok", "data": _serialize_instance(target)}

            if self.action == "merge":
                identifier, keys = _resolve_identifier(ctx_map, payload)
                target = _find_by_identifier(identifier, keys, payload)
                if target is None:
                    target = _find_by_payload(payload)
                if target is None:
                    target = model(**payload)
                    if not getattr(target, alias_field, None):
                        setattr(target, alias_field, getattr(target, "id", None))
                    storage.append(target)
                for key, value in payload.items():
                    setattr(target, key, value)
                return {"status": "ok", "data": _serialize_instance(target)}

            if self.action == "delete":
                identifier, keys = _resolve_identifier(ctx_map, payload)
                target = _find_by_identifier(identifier, keys, payload)
                if target is None:
                    raise HTTPException(status_code=404, detail="Item not found")
                storage.remove(target)
                return {"status": "ok"}

            return {"status": "ok"}

    model.handlers = SimpleNamespace(
        create=_Handler("create"),
        list=_Handler("list"),
        read=_Handler("read"),
        update=_Handler("update"),
        replace=_Handler("replace"),
        merge=_Handler("merge"),
        delete=_Handler("delete"),
    )


class TigrblApp(FastAPI):
    def __init__(self, *, engine: Mapping[str, Any] | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.engine = engine

    def include_model(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> tuple[type, APIRouter]:
        router = self._register_model(
            model, base_prefix=prefix, mount_router=mount_router
        )
        return model, router

    def include_models(
        self,
        models: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, APIRouter]:
        registered: Dict[str, APIRouter] = {}
        for model in models:
            registered[model.__name__] = self._register_model(
                model, base_prefix=base_prefix, mount_router=mount_router
            )
        return registered

    def _register_model(
        self, model: type, *, base_prefix: str | None = None, mount_router: bool = True
    ) -> APIRouter:
        _ensure_model_handlers(model)
        resource = _resource_name(model)
        base = ""
        if base_prefix:
            base = "/" + base_prefix.strip("/")
        prefix = re.sub(r"/{2,}", "/", f"{base}/{resource}") or f"/{resource}"
        router = APIRouter(prefix=prefix)

        @router.post("")
        async def create_item(
            payload: Mapping[str, Any] = Body(default={}),
        ):  # pragma: no cover - dynamic
            ctx = {"payload": dict(payload or {})}
            return await model.handlers.create.handler(ctx)

        @router.get("")
        async def list_items():  # pragma: no cover - dynamic
            return await model.handlers.list.handler({})

        @router.get("/{item_id}")
        async def read_item(item_id: str):  # pragma: no cover - dynamic
            ctx = {"path_params": {"item_id": item_id}}
            return await model.handlers.read.handler(ctx)

        @router.patch("/{item_id}")
        async def update_item(
            item_id: str, payload: Mapping[str, Any] = Body(default={})
        ):  # pragma: no cover - dynamic
            ctx = {"path_params": {"item_id": item_id}, "payload": dict(payload or {})}
            return await model.handlers.update.handler(ctx)

        @router.delete("/{item_id}")
        async def delete_item(item_id: str):  # pragma: no cover - dynamic
            ctx = {"path_params": {"item_id": item_id}}
            return await model.handlers.delete.handler(ctx)

        for entry in _REGISTERED_API_OPS.get(model, []):
            alias = entry.get("alias")
            func = entry.get("func")
            if not alias or func is None:
                continue

            @router.post(f"/{alias}")
            async def _custom_op(
                payload: Mapping[str, Any] = Body(default={}),
                _func: Callable[..., Any] = func,
            ):  # pragma: no cover - dynamic
                ctx = {"payload": dict(payload or {})}
                result = _func(model, ctx)
                if inspect.isawaitable(result):
                    result = await result
                return result

        if mount_router:
            self.include_router(router)
        model.rest = SimpleNamespace(router=router)
        return router


tigrbl_module.TigrblApp = TigrblApp

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
ApplicationFee = make_model("ApplicationFee", ["external_id", "refunded"])
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
        "external_id",
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
        "external_id",
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
Product = make_model("Product", ["external_id", "name", "description", "metadata"])
Price = make_model("Price", ["external_id", "unit_amount"])
PriceTier = make_model("PriceTier", ["price_id", "up_to", "unit_amount"])
Customer = make_model(
    "Customer",
    [
        "email",
        "name",
        "external_id",
        "default_payment_method_ref",
        "tax_exempt",
        "metadata",
        "active",
    ],
)
SubscriptionItem = make_model(
    "SubscriptionItem",
    ["subscription_id", "external_id", "quantity", "price_id"],
)
InvoiceLineItem = make_model(
    "InvoiceLineItem",
    ["invoice_id", "stripe_invoice_line_item_id", "amount", "description"],
)
Refund = make_model("Refund", ["external_id", "amount"])
ConnectedAccount = make_model("ConnectedAccount", ["external_id", "details_submitted"])
Transfer = make_model("Transfer", ["external_id", "amount", "currency"])
Feature = make_model("Feature", ["feature_key", "name", "description"])
PriceFeatureEntitlement = make_model(
    "PriceFeatureEntitlement", ["price_id", "feature_id", "entitlement"]
)
CheckoutSession = make_model("CheckoutSession", ["external_id", "status"])
CustomerAccountLink = make_model(
    "CustomerAccountLink", ["customer_id", "connected_account_id"]
)
SplitRule = make_model("SplitRule", ["name", "percentage"])
WebhookEndpoint = make_model("WebhookEndpoint", ["url", "description"])
CreditUsagePolicy = make_model("CreditUsagePolicy", ["policy_key", "limit"])
CreditLedger = make_model("CreditLedger", ["balance_id", "delta"])

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
_register_module(
    "tigrbl_billing.tables.credit_ledger",
    CreditLedger=CreditLedger,
    LedgerDirection=LedgerDirection,
)
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
_register_module("tigrbl_billing.tables.feature", Feature=Feature)
_register_module(
    "tigrbl_billing.tables.price_feature_entitlement",
    PriceFeatureEntitlement=PriceFeatureEntitlement,
)
_register_module(
    "tigrbl_billing.tables.invoice_line_item", InvoiceLineItem=InvoiceLineItem
)
_register_module("tigrbl_billing.tables.refund", Refund=Refund)
_register_module(
    "tigrbl_billing.tables.connected_account", ConnectedAccount=ConnectedAccount
)
_register_module(
    "tigrbl_billing.tables.customer_account_link",
    CustomerAccountLink=CustomerAccountLink,
)
_register_module("tigrbl_billing.tables.transfer", Transfer=Transfer)
_register_module("tigrbl_billing.tables.split_rule", SplitRule=SplitRule)
_register_module(
    "tigrbl_billing.tables.usage_rollup",
    UsageRollup=UsageRollup,
)
_register_module(
    "tigrbl_billing.tables.stripe_event_log",
    StripeEventLog=StripeEventLog,
    EventProcessStatus=EventProcessStatus,
)
_register_module(
    "tigrbl_billing.tables.checkout_session", CheckoutSession=CheckoutSession
)
_register_module(
    "tigrbl_billing.tables.webhook_endpoint", WebhookEndpoint=WebhookEndpoint
)
_register_module(
    "tigrbl_billing.tables.credit_usage_policy", CreditUsagePolicy=CreditUsagePolicy
)


# ----------------------------------------------------------------------------
# Shared helpers for tests
# ----------------------------------------------------------------------------


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(sock.getsockname()[1])


@contextlib.asynccontextmanager
async def run_uvicorn_app(app: FastAPI):
    port = _get_free_port()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        loop="asyncio",
        lifespan="on",
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    try:
        for _ in range(100):
            if server.started:
                break
            await asyncio.sleep(0.05)
        else:
            raise RuntimeError("uvicorn server did not start")

        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}") as client:
            yield client
    finally:
        server.should_exit = True
        if thread.is_alive():
            thread.join(timeout=5)


@pytest.fixture
def uvicorn_client():
    return run_uvicorn_app


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
