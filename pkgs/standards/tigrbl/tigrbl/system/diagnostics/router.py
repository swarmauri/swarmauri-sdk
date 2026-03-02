from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable, Optional

from ..._spec.binding_spec import HttpRestBindingSpec
from ..._spec.op_spec import OpSpec
from ...mapping.model_helpers import _OpSpecGroup
from ..._concrete._router import Router
from .healthz import build_healthz_endpoint
from .hookz import build_hookz_endpoint
from .kernelz import build_kernelz_endpoint
from .methodz import build_methodz_endpoint
from .utils import opspecs, table_iter


def _register_runtime_diagnostics_op(
    router: Any,
    *,
    path: str,
    alias: str,
    endpoint_factory: Callable[[Any], Any],
) -> None:
    """Expose diagnostics endpoints to the kernel runtime operation plan."""
    tables = getattr(router, "tables", None)
    if not isinstance(tables, dict):
        return

    model_name = "__tigrbl_system_docs__"
    model = tables.get(model_name)
    if model is None:
        model = type("TigrblSystemDocs", (), {})
        model.resource_name = "system_docs"
        model.hooks = SimpleNamespace()
        model.ops = SimpleNamespace(by_alias={})
        model.opspecs = SimpleNamespace(all=())
        tables[model_name] = model

    binding = HttpRestBindingSpec(proto="http.rest", path=path, methods=("GET",))
    existing_specs = tuple(model.ops.by_alias.get(alias, ()) or ())
    existing = existing_specs[0] if existing_specs else None

    if existing is not None:
        merged_bindings = list(tuple(getattr(existing, "bindings", ()) or ()))
        if binding not in merged_bindings:
            merged_bindings.append(binding)
        op = replace(existing, bindings=tuple(merged_bindings))
    else:
        op = OpSpec(
            alias=alias,
            target="read",
            arity="collection",
            persist="skip",
            expose_routes=False,
            bindings=(binding,),
        )

    model.ops.by_alias[alias] = _OpSpecGroup((op,))
    model.opspecs.all = tuple(
        spec for spec in model.opspecs.all if getattr(spec, "alias", None) != alias
    ) + (op,)

    async def _runtime_diagnostics_step(ctx: Any) -> None:
        payload = await endpoint_factory(ctx)
        setattr(ctx, "result", payload)
        if isinstance(getattr(ctx, "temp", None), dict):
            ctx.temp.setdefault("egress", {})["result"] = payload

    hooks_ns = getattr(model.hooks, alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, alias, hooks_ns)
    hooks_ns.HANDLER = [_runtime_diagnostics_step]


def _register_runtime_paths(
    router: Any, *, path: str, alias: str, endpoint_factory: Callable[[Any], Any]
) -> None:
    _register_runtime_diagnostics_op(
        router,
        path=path,
        alias=alias,
        endpoint_factory=endpoint_factory,
    )
    system_prefix = str(getattr(router, "system_prefix", "/system") or "/system")
    if system_prefix and system_prefix != "/":
        prefixed = f"{system_prefix.rstrip('/')}{path}"
        _register_runtime_diagnostics_op(
            router,
            path=prefixed,
            alias=alias,
            endpoint_factory=endpoint_factory,
        )


def mount_diagnostics(
    router: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
) -> Router:
    """
    Create & return a Router that exposes:
      GET /healthz
      GET /methodz
      GET /hookz
      GET /kernelz
    """
    source_router = router
    router = Router()

    dep = get_db

    healthz_endpoint = build_healthz_endpoint(dep)

    async def _runtime_healthz(ctx: Any) -> Any:
        del ctx
        return {"ok": True}

    _register_runtime_paths(
        source_router,
        path="/healthz",
        alias="healthz",
        endpoint_factory=_runtime_healthz,
    )
    router.add_route(
        "/healthz",
        healthz_endpoint,
        methods=["GET"],
        name="healthz",
        tags=["system"],
        summary="Health",
        description="Database connectivity check.",
    )

    methodz_endpoint = build_methodz_endpoint(source_router)
    _register_runtime_paths(
        source_router,
        path="/methodz",
        alias="methodz",
        endpoint_factory=lambda _ctx: methodz_endpoint(),
    )
    router.add_route(
        "/methodz",
        methodz_endpoint,
        methods=["GET"],
        name="methodz",
        tags=["system"],
        summary="Methods",
        description="Ordered, canonical operation list.",
    )

    hookz_endpoint = build_hookz_endpoint(source_router)
    _register_runtime_paths(
        source_router,
        path="/hookz",
        alias="hookz",
        endpoint_factory=lambda _ctx: hookz_endpoint(),
    )
    router.add_route(
        "/hookz",
        hookz_endpoint,
        methods=["GET"],
        name="hookz",
        tags=["system"],
        summary="Hooks",
        description=(
            "Expose hook execution order for each method.\n\n"
            "Phases appear in runner order; error phases trail.\n"
            "Within each phase, hooks are listed in execution order: "
            "global (None) hooks, then method-specific hooks."
        ),
    )

    kernelz_endpoint = build_kernelz_endpoint(source_router)

    async def _runtime_kernelz(_ctx: Any) -> Any:
        from ...runtime.kernel import _default_kernel as K

        K.ensure_primed(source_router)
        payload: dict[str, dict[str, list[str]]] = {}
        for model in table_iter(source_router):
            model_name = getattr(model, "__name__", str(model))
            payload[model_name] = {}
            for sp in opspecs(model):
                payload[model_name][sp.alias] = K.plan_labels(model, sp.alias)
        return payload

    _register_runtime_paths(
        source_router,
        path="/kernelz",
        alias="kernelz",
        endpoint_factory=_runtime_kernelz,
    )
    router.add_route(
        "/kernelz",
        kernelz_endpoint,
        methods=["GET"],
        name="kernelz",
        tags=["system"],
        summary="Kernel Plan",
        description="Phase-chain plan as built by the kernel per operation.",
    )

    return router


__all__ = ["mount_diagnostics"]
