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
    "mapping": "tigrbl_canon.mapping",
    "orm": "tigrbl_orm.orm",
    "runtime": "tigrbl_runtime.runtime",
    "executors": "tigrbl_runtime.executors",
    "atoms": "tigrbl_atoms.atoms",
    "kernel": "tigrbl_kernel.kernel",
}


def _optional_import(path: str):
    try:
        return import_module(path)
    except ImportError:
        return None


for alias, target in _ALIAS_MODULES.items():
    module = _optional_import(target)
    if module is not None:
        sys.modules.setdefault(f"{__name__}.{alias}", module)


_spec = import_module("tigrbl_core._spec")
_base = import_module("tigrbl_base._base")
_concrete = import_module("tigrbl_concrete._concrete")
canon = import_module("tigrbl_canon.mapping")
orm = import_module("tigrbl_orm.orm")
runtime = _optional_import("tigrbl_runtime.runtime")
atoms = _optional_import("tigrbl_atoms.atoms")
kernel = _optional_import("tigrbl_kernel.kernel")
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

bind = canon.bind
rebind = canon.rebind
build_schemas = canon.build_schemas
build_hooks = canon.build_hooks
build_handlers = canon.build_handlers
register_rpc = canon.register_rpc
build_rest = canon.build_rest
include_table = canon.include_table
include_tables = canon.include_tables
rpc_call = canon.rpc_call

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
    "include_table",
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
