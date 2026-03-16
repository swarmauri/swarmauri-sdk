from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any
from typing import Callable, Optional, Sequence

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.engine_spec import EngineCfg
from tigrbl_core._spec.response_spec import ResponseSpec


@dataclass(eq=False)
class AppBase(AppSpec):
    """Base app configuration helpers shared by concrete app implementations."""

    title: str = "Tigrbl"
    description: str | None = None
    version: str = "0.1.0"
    engine: Optional[EngineCfg] = None
    routers: Sequence[Any] = ()
    ops: Sequence[Any] = ()
    tables: Sequence[Any] = ()
    schemas: Sequence[Any] = ()
    hooks: Sequence[Callable[..., Any]] = ()
    security_deps: Sequence[Callable[..., Any]] = ()
    deps: Sequence[Callable[..., Any]] = ()
    response: Optional[ResponseSpec] = None
    jsonrpc_prefix: str = "/rpc"
    system_prefix: str = "/system"
    middlewares: Sequence[Any] = ()
    lifespan: Optional[Callable[..., Any]] = None

    @staticmethod
    def _is_bindable_child_class(candidate: Any) -> bool:
        if not inspect.isclass(candidate):
            return False

        bindable_types: list[type[Any]] = []
        for mod_name, type_name in (
            ("._table_base", "TableBase"),
            ("._op_base", "OpBase"),
            ("._hook_base", "HookBase"),
            ("._schema_base", "SchemaBase"),
        ):
            try:
                module = __import__(
                    f"tigrbl_base._base{mod_name}", fromlist=[type_name]
                )
                bindable = getattr(module, type_name, None)
                if isinstance(bindable, type):
                    bindable_types.append(bindable)
            except Exception:
                continue

        if not bindable_types:
            return False

        try:
            return issubclass(candidate, tuple(bindable_types))
        except TypeError:
            return False

    @classmethod
    def _bind_child_to_parent(cls, child: Any, *, parent: object | None) -> Any:
        if parent is None:
            return child

        target = child
        if cls._is_bindable_child_class(child):
            try:
                target = child()
            except Exception:
                target = child

        for attr in ("app", "parent", "owner"):
            if hasattr(target, attr):
                try:
                    setattr(target, attr, parent)
                except Exception:
                    pass

        for attr in ("APP", "PARENT", "OWNER"):
            if hasattr(target, attr):
                try:
                    setattr(target, attr, parent)
                except Exception:
                    pass

        return target

    @classmethod
    def collect_spec(cls, app: type) -> AppSpec:
        """Collect and normalize an ``AppSpec`` snapshot from an app type."""

        spec = AppSpec.collect(app)
        routers = tuple(dict.fromkeys(tuple(spec.routers or ())))
        return AppSpec(
            title=spec.title,
            description=spec.description,
            version=spec.version,
            engine=spec.engine,
            routers=routers,
            ops=tuple(spec.ops or ()),
            tables=tuple(spec.tables or ()),
            schemas=tuple(spec.schemas or ()),
            hooks=tuple(spec.hooks or ()),
            security_deps=tuple(spec.security_deps or ()),
            deps=tuple(spec.deps or ()),
            response=spec.response,
            jsonrpc_prefix=spec.jsonrpc_prefix,
            system_prefix=spec.system_prefix,
            middlewares=tuple(spec.middlewares or ()),
            lifespan=spec.lifespan,
        )

    @classmethod
    def _bind_mapped_children(
        cls, children: Sequence[Any] | None, *, parent: object | None
    ) -> tuple[Any, ...]:
        return tuple(
            cls._bind_child_to_parent(child, parent=parent)
            for child in tuple(children or ())
        )

    @classmethod
    def bind_spec(cls, spec: AppSpec, *, parent: object | None = None) -> AppSpec:
        """Bind a collected AppSpec by attaching mapped children to the parent."""

        return AppSpec(
            title=str(spec.title or "Tigrbl"),
            description=spec.description,
            version=str(spec.version or "0.1.0"),
            engine=spec.engine,
            routers=cls._bind_mapped_children(spec.routers, parent=parent),
            ops=cls._bind_mapped_children(spec.ops, parent=parent),
            tables=cls._bind_mapped_children(spec.tables, parent=parent),
            schemas=cls._bind_mapped_children(spec.schemas, parent=parent),
            hooks=cls._bind_mapped_children(spec.hooks, parent=parent),
            security_deps=tuple(spec.security_deps or ()),
            deps=tuple(spec.deps or ()),
            response=spec.response,
            jsonrpc_prefix=str(spec.jsonrpc_prefix or "/rpc"),
            system_prefix=str(spec.system_prefix or "/system"),
            middlewares=tuple(spec.middlewares or ()),
            lifespan=spec.lifespan,
        )


__all__ = ["AppBase"]
