from __future__ import annotations

from typing import Any

from ._table_registry import TableRegistry
from .._spec.app_spec import AppSpec
from ..ddl import initialize as _ddl_initialize
from .._concrete._engine import Engine
from ..mapping import engine_resolver as _resolver
from .._spec.engine_spec import EngineCfg
from ._routing import (
    include_router as _include_router_impl,
    merge_tags as _merge_tags_impl,
    normalize_prefix as _normalize_prefix_impl,
)
import json

from ..runtime.executor import _Ctx, _invoke
from ..runtime.kernel.core import Kernel
from ..runtime.kernel.models import OpKey
from ..runtime.gw.raw import GwRawEnvelope


class App(AppSpec):
    @classmethod
    def _collect_mro_spec(cls) -> AppSpec:
        return AppSpec.collect(cls)

    TITLE = "Tigrbl"
    VERSION = "0.1.0"
    LIFESPAN = None
    ROUTERS = ()
    OPS = ()
    TABLES = ()
    SCHEMAS = ()
    HOOKS = ()
    DESCRIPTION = None
    OPENAPI_URL = "/openapi.json"
    DOCS_URL = "/docs"
    DEBUG = False
    SWAGGER_UI_VERSION = "5.31.0"
    SECURITY_DEPS = ()
    DEPS = ()
    RESPONSE = None
    JSONRPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

    def __init__(self, *, engine: EngineCfg | None = None, **asgi_kwargs: Any) -> None:
        collected_spec = self.__class__._collect_mro_spec()

        title = asgi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        else:
            title = collected_spec.title
        version = asgi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        else:
            version = collected_spec.version
        lifespan = asgi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        else:
            lifespan = collected_spec.lifespan
        get_db = asgi_kwargs.pop("get_db", None)
        if get_db is not None:
            self.get_db = get_db
        description = asgi_kwargs.pop("description", None)
        if description is None:
            description = getattr(self, "DESCRIPTION", None)
        openapi_url = asgi_kwargs.pop("openapi_url", None)
        if openapi_url is None:
            openapi_url = getattr(self, "OPENAPI_URL", "/openapi.json")
        docs_url = asgi_kwargs.pop("docs_url", None)
        if docs_url is None:
            docs_url = getattr(self, "DOCS_URL", "/docs")
        debug = asgi_kwargs.pop("debug", None)
        if debug is None:
            debug = bool(getattr(self, "DEBUG", False))
        swagger_ui_version = asgi_kwargs.pop("swagger_ui_version", None)
        if swagger_ui_version is None:
            swagger_ui_version = getattr(self, "SWAGGER_UI_VERSION", "5.31.0")
        include_docs = asgi_kwargs.pop("include_docs", None)
        if include_docs is None:
            include_docs = bool(getattr(self, "INCLUDE_DOCS", False))
        self.title = title
        self.version = version
        self.description = description
        self.openapi_url = openapi_url
        self.docs_url = docs_url
        self.debug = debug
        self.swagger_ui_version = swagger_ui_version
        self.engine = engine if engine is not None else collected_spec.engine
        self.routers = tuple(collected_spec.routers)
        self.ops = tuple(collected_spec.ops)
        self.tables = TableRegistry(tables=collected_spec.tables)
        self.schemas = tuple(collected_spec.schemas)
        self.hooks = tuple(collected_spec.hooks)
        self.security_deps = tuple(collected_spec.security_deps)
        self.deps = tuple(collected_spec.deps)
        self.response = collected_spec.response
        self.jsonrpc_prefix = collected_spec.jsonrpc_prefix
        self.system_prefix = collected_spec.system_prefix
        self.lifespan = lifespan

        from ._router import Router

        Router.__init__(
            self,
            engine=self.engine,
            title=self.title,
            version=self.version,
            description=self.description,
            openapi_url=self.openapi_url,
            docs_url=self.docs_url,
            debug=self.debug,
            swagger_ui_version=self.swagger_ui_version,
            include_docs=include_docs,
            **asgi_kwargs,
        )
        self._kernel = Kernel()
        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()

    @property
    def router(self) -> "App":
        return self

    def install_engines(
        self, *, router: Any = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        routers = (router,) if router is not None else self.ROUTERS
        tables = tables if tables is not None else self.TABLES
        if routers:
            for a in routers:
                Engine.install_from_objects(app=self, router=a, tables=tuple(tables))
        else:
            Engine.install_from_objects(app=self, router=None, tables=tuple(tables))

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
        await self.invoke(env)

    async def invoke(self, env: GwRawEnvelope) -> None:
        scope_type = env.scope.get("type")

        if scope_type == "lifespan":
            await self._handle_lifespan(env)
            return

        if scope_type != "http":
            return

        plan = self._kernel.kernel_plan(self)
        ctx = _Ctx.ensure(request=None, db=None)
        ctx.app = self
        ctx.router = self
        ctx.raw = env
        ctx.kernel_plan = plan

        for phase in ("INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE"):
            for step in plan.ingress_chain.get(phase, ()):
                result = step(None, ctx)
                if hasattr(result, "__await__"):
                    await result

        proto = getattr(ctx, "proto", None)
        selector = getattr(ctx, "selector", None)
        route = ctx.temp.get("route", {}) if isinstance(ctx.temp, dict) else {}
        if not isinstance(proto, str):
            proto = route.get("protocol", proto)
        if not isinstance(selector, str):
            selector = route.get("selector", selector)
        if (
            not isinstance(selector, str)
            and isinstance(proto, str)
            and proto.endswith(".rest")
        ):
            gw_raw = getattr(ctx, "gw_raw", None)
            method = getattr(gw_raw, "method", None)
            path = getattr(gw_raw, "path", None)
            if isinstance(method, str) and isinstance(path, str):
                selector = f"{method.upper()} {path}"
        if (
            not isinstance(selector, str)
            and isinstance(proto, str)
            and proto.endswith(".jsonrpc")
        ):
            selector = route.get("rpc_method")

        if not isinstance(proto, str) or not isinstance(selector, str):
            await self._send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        opmeta_index = plan.opkey_to_meta.get(OpKey(proto=proto, selector=selector))
        if not isinstance(opmeta_index, int) or not (
            0 <= opmeta_index < len(plan.opmeta)
        ):
            await self._send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        opmeta = plan.opmeta[opmeta_index]
        ctx.model = opmeta.model
        ctx.op = opmeta.alias
        ctx.opview = self._kernel.get_opview(self, opmeta.model, opmeta.alias)
        ctx.proto = proto
        ctx.selector = selector

        phases = dict(plan.phase_chains.get(opmeta_index, {}))
        phases["INGRESS_BEGIN"] = []
        phases["INGRESS_PARSE"] = []
        phases["INGRESS_ROUTE"] = []

        await _invoke(request=None, db=None, phases=phases, ctx=ctx)

        egress = ctx.temp.get("egress", {}) if isinstance(ctx.temp, dict) else {}
        response = (
            egress.get("transport_response") if isinstance(egress, dict) else None
        )
        if isinstance(response, dict):
            await self._send_transport_response(env, response)
            return

        status = int(getattr(ctx, "status_code", 200) or 200)
        body = getattr(ctx, "result", None)
        await self._send_json(env, status, body)

    async def _send_transport_response(
        self, env: GwRawEnvelope, response: dict[str, Any]
    ) -> None:
        status = int(response.get("status_code", 200) or 200)
        headers_obj = response.get("headers")
        headers: list[tuple[bytes, bytes]] = []
        if isinstance(headers_obj, dict):
            headers = [
                (str(k).encode("latin-1"), str(v).encode("latin-1"))
                for k, v in headers_obj.items()
            ]
        body = response.get("body", b"")
        if isinstance(body, str):
            body = body.encode("utf-8")
        elif body is None:
            body = b""
        elif not isinstance(body, (bytes, bytearray)):
            body = json.dumps(body).encode("utf-8")

        await env.send(
            {"type": "http.response.start", "status": status, "headers": headers}
        )
        await env.send(
            {"type": "http.response.body", "body": bytes(body), "more_body": False}
        )

    async def _send_json(self, env: GwRawEnvelope, status: int, payload: Any) -> None:
        await env.send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await env.send(
            {
                "type": "http.response.body",
                "body": json.dumps(payload).encode("utf-8"),
                "more_body": False,
            }
        )

    async def _handle_lifespan(self, env: GwRawEnvelope) -> None:
        while True:
            message = await env.receive()
            message_type = message.get("type")
            if message_type == "lifespan.startup":
                await self.run_event_handlers("startup")
                await env.send({"type": "lifespan.startup.complete"})
                continue
            if message_type == "lifespan.shutdown":
                await self.run_event_handlers("shutdown")
                await env.send({"type": "lifespan.shutdown.complete"})
            return

    def _normalize_prefix(self, prefix: str) -> str:
        return _normalize_prefix_impl(prefix)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return _merge_tags_impl(getattr(self, "tags", None), tags)

    def include_router(self, router: Any, *, prefix: str | None = None) -> Any:
        routed = getattr(router, "router", router)
        _include_router_impl(self, routed, prefix=prefix or "")
        return router

    initialize = _ddl_initialize
