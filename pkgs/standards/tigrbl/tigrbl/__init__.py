"""Tigrbl public API facade over split core packages."""

from __future__ import annotations

from importlib import import_module
from pkgutil import extend_path
import sys

__path__ = extend_path(__path__, __name__)


# Compatibility aliases so legacy ``tigrbl.<segment>`` imports resolve to
# the new split packages.
_ALIAS_MODULES = {
    "_spec": "tigrbl_core._spec",
    "_base": "tigrbl_base._base",
    "_concrete": "tigrbl_concrete._concrete",
    "core": "tigrbl_ops_oltp",
    "runtime": "tigrbl_runtime.runtime",
    "executors": "tigrbl_runtime.executors",
    "atoms": "tigrbl_atoms.atoms",
}


def _optional_import(path: str):
    try:
        return import_module(path)
    except ImportError:
        return None


def _install_alias(alias: str, target: str) -> None:
    module = _optional_import(target)
    if module is None:
        return

    alias_name = f"{__name__}.{alias}"
    sys.modules.setdefault(alias_name, module)

    target_prefix = f"{target}."
    alias_prefix = f"{alias_name}."
    for name, loaded in tuple(sys.modules.items()):
        if name.startswith(target_prefix):
            suffix = name[len(target_prefix) :]
            sys.modules.setdefault(f"{alias_prefix}{suffix}", loaded)

    module_path = getattr(module, "__path__", None)
    if not module_path:
        return

    from pkgutil import walk_packages

    for info in walk_packages(module_path, target_prefix):
        submodule = _optional_import(info.name)
        if submodule is None:
            continue
        suffix = info.name[len(target_prefix) :]
        sys.modules.setdefault(f"{alias_prefix}{suffix}", submodule)


for alias, target in _ALIAS_MODULES.items():
    _install_alias(alias, target)


_spec = import_module("tigrbl_core._spec")
_base = import_module("tigrbl_base._base")
_concrete = import_module("tigrbl_concrete._concrete")
canon = None
orm = import_module("tigrbl_orm.orm")
runtime = _optional_import("tigrbl_runtime.runtime")
atoms = _optional_import("tigrbl_atoms.atoms")
kernel = None
core = _optional_import("tigrbl_ops_oltp")

# Backward-compatible names requested for top-level facade access.
specs = _spec
base = _base
concrete = _concrete

from tigrbl_concrete._concrete import (  # noqa: E402
    APIKey,
    Alias,
    App,
    BackgroundTask,
    Column,
    FileResponse,
    ForeignKey,
    Hook,
    HTMLResponse,
    HTTPBearer,
    JSONResponse,
    MutualTLS,
    OAuth2,
    OpenIdConnect,
    Op,
    PlainTextResponse,
    RedirectResponse,
    Request,
    Response,
    Route,
    Router,
    Schema,
    StorageTransform,
    StreamingResponse,
    Table,
    TableRegistry,
    TigrblApp,
    TigrblRouter,
)
from tigrbl_concrete._concrete.dependencies import Depends  # noqa: E402
from tigrbl_runtime.runtime.status.exceptions import HTTPException  # noqa: E402
from tigrbl.engine import resolver  # noqa: E402
from tigrbl.system import mount_diagnostics  # noqa: E402
from tigrbl_core.config.constants import DEFAULT_HTTP_METHODS, HOOK_DECLS_ATTR  # noqa: E402
from tigrbl.decorators import (  # noqa: E402
    alias,
    allow_anon,
    alias_ctx,
    engine_ctx,
    hook_ctx,
    middleware,
    middlewares,
    op_alias,
    op_ctx,
    response_ctx,
    route_ctx,
    schema_ctx,
)
from tigrbl.shortcuts.op import op  # noqa: E402
from tigrbl.schema import _build_list_params, _build_schema, get_schema  # noqa: E402
from tigrbl.ddl import bootstrap_dbschema, ensure_schemas, register_sqlite_attach  # noqa: E402

from tigrbl_base._base import (  # noqa: E402
    AppBase,
    ForeignKeyBase,
    HookBase,
    RouterBase,
    TableBase,
    TableRegistryBase,
)
from tigrbl_core._spec import (  # noqa: E402
    AppSpec,
    Arity,
    ColumnSpec,
    EngineSpec,
    FieldSpec,
    ForeignKeySpec,
    HookPhase,
    IOSpec,
    OpSpec,
    PersistPolicy,
    PHASE,
    PHASES,
    RequestSpec,
    ResponseSpec,
    RouterSpec,
    SchemaArg,
    SchemaRef,
    SchemaSpec,
    SessionSpec,
    StorageSpec,
    StorageTransformSpec,
    TableRegistrySpec,
    TableSpec,
    TargetOp,
    TemplateSpec,
)
from tigrbl_runtime.runtime.executor import _invoke  # noqa: E402


def bind(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model").bind(*args, **kwargs)


def rebind(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model").rebind(*args, **kwargs)


def build_schemas(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model")._materialize_schemas(
        *args, **kwargs
    )


def build_hooks(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.model")._bind_model_hooks(
        *args, **kwargs
    )


def build_handlers(*args, **kwargs):
    mod = import_module("tigrbl_concrete._mapping.model")
    specs = mod._materialize_handlers(*args, **kwargs)
    model = args[0] if args else kwargs.get("model")
    spec_arg = args[1] if len(args) > 1 else kwargs.get("specs", ())
    spec_tuple = tuple(spec_arg or ())
    if model is not None:
        mod._bind_model_hooks(model, spec_tuple)
    return specs


def register_rpc(*args, **kwargs):
    return import_module("tigrbl_base._base._rpc_map").register_and_attach(
        *args, **kwargs
    )


def build_rest(*args, **kwargs):
    if "router" not in kwargs:
        kwargs["router"] = None
    return import_module("tigrbl_concrete._mapping.model")._materialize_rest_router(
        *args, **kwargs
    )


def include_tables(*args, **kwargs):
    return import_module("tigrbl_concrete._mapping.router.include").include_tables(
        *args, **kwargs
    )


async def rpc_call(*args, **kwargs):
    return await import_module("tigrbl_concrete._mapping.router.rpc").rpc_call(
        *args, **kwargs
    )


__all__ = [
    "specs",
    "base",
    "concrete",
    "canon",
    "orm",
    "runtime",
    "atoms",
    "kernel",
    "core",
    "TigrblApp",
    "TigrblRouter",
    "Router",
    "Depends",
    "HTTPException",
    "TableBase",
    "RouterBase",
    "Op",
    "op",
    "HTTPBearer",
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
    "OpSpec",
    "TargetOp",
    "Arity",
    "PersistPolicy",
    "PHASE",
    "PHASES",
    "HookPhase",
    "SchemaRef",
    "SchemaArg",
    "alias_ctx",
    "op_ctx",
    "route_ctx",
    "hook_ctx",
    "schema_ctx",
    "response_ctx",
    "alias",
    "allow_anon",
    "Alias",
    "op_alias",
    "engine_ctx",
    "ResponseSpec",
    "bind",
    "rebind",
    "build_schemas",
    "build_hooks",
    "build_handlers",
    "register_rpc",
    "build_rest",
    "include_tables",
    "rpc_call",
    "_invoke",
    "_build_schema",
    "_build_list_params",
    "get_schema",
    "mount_diagnostics",
    "ensure_schemas",
    "register_sqlite_attach",
    "bootstrap_dbschema",
    "DEFAULT_HTTP_METHODS",
    "Request",
    "Response",
    "JSONResponse",
    "BackgroundTask",
    "resolver",
    "AppSpec",
    "RouterSpec",
    "TableSpec",
    "TableRegistrySpec",
    "ColumnSpec",
    "FieldSpec",
    "IOSpec",
    "StorageSpec",
    "StorageTransform",
    "StorageTransformSpec",
    "ForeignKeySpec",
    "RequestSpec",
    "SchemaSpec",
    "SessionSpec",
    "EngineSpec",
    "TemplateSpec",
    "ForeignKeyBase",
    "HookBase",
    "TableRegistryBase",
    "AppBase",
    "App",
    "Table",
    "Column",
    "Route",
    "Schema",
    "Hook",
    "ForeignKey",
    "TableRegistry",
    "HOOK_DECLS_ATTR",
    "middleware",
    "middlewares",
    "FileResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "StreamingResponse",
    "RedirectResponse",
]
