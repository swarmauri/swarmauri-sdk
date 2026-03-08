from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.binding_spec import (
    BindingRegistrySpec,
    BindingSpec,
    HttpRestBindingSpec,
)
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.engine_spec import EngineCfg
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.response_spec import ResponseSpec
from tigrbl_core._spec.serde import SerdeMixin
from tigrbl_core._spec.storage_spec import ForeignKeySpec, StorageSpec


class ExampleClass:
    pass


@dataclass(eq=False)
class ConcreteAppSpec(AppSpec):
    title: str = "Tigrbl"
    description: str | None = None
    version: str = "0.1.0"
    engine: EngineCfg | None = None
    routers: tuple[Any, ...] = ()
    ops: tuple[Any, ...] = ()
    tables: tuple[Any, ...] = ()
    schemas: tuple[Any, ...] = ()
    hooks: tuple[Any, ...] = ()
    security_deps: tuple[Any, ...] = ()
    deps: tuple[Any, ...] = ()
    response: ResponseSpec | None = None
    jsonrpc_prefix: str = "/rpc"
    system_prefix: str = "/system"
    middlewares: tuple[Any, ...] = ()
    lifespan: Any | None = None


def test_column_spec_json_round_trip_restores_nested_specs() -> None:
    spec = ColumnSpec(
        storage=StorageSpec(
            type_=ExampleClass,
            nullable=False,
            fk=ForeignKeySpec(target="widgets.id", on_delete="CASCADE"),
        ),
        field=FieldSpec(py_type=str, constraints={"max_length": 50}),
        io=IOSpec(in_verbs=("create",), out_verbs=("read",)),
    )

    restored = ColumnSpec.from_json(spec.to_json())

    assert isinstance(restored.storage, StorageSpec)
    assert restored.storage is not None
    assert restored.storage.type_ is ExampleClass
    assert restored.storage.fk is not None
    assert restored.storage.fk.target == "widgets.id"
    assert restored.field.constraints == {"max_length": 50}
    assert restored.io.in_verbs == ("create",)


def test_app_spec_toml_round_trip_preserves_scalars() -> None:
    spec = ConcreteAppSpec(
        title="Serde App",
        description="serializable",
        version="1.2.3",
        jsonrpc_prefix="/rpcz",
        system_prefix="/systemz",
    )

    restored = ConcreteAppSpec.from_toml(spec.to_toml())

    assert restored.title == "Serde App"
    assert restored.description == "serializable"
    assert restored.version == "1.2.3"
    assert restored.jsonrpc_prefix == "/rpcz"
    assert restored.system_prefix == "/systemz"


def test_column_spec_yaml_round_trip_preserves_nested_foreign_key() -> None:
    spec = ColumnSpec(
        storage=StorageSpec(
            type_=str,
            nullable=True,
            fk=ForeignKeySpec(target="parents.id"),
        ),
        field=FieldSpec(py_type=str),
        io=IOSpec(out_verbs=("list",)),
    )

    restored = ColumnSpec.from_yaml(spec.to_yaml())

    assert restored.storage is not None
    assert restored.storage.fk is not None
    assert restored.storage.fk.target == "parents.id"
    assert restored.io.out_verbs == ("list",)


def test_binding_spec_inherits_serde_mixin_and_round_trips() -> None:
    spec = BindingSpec(
        name="list_widgets",
        spec=HttpRestBindingSpec(
            proto="http.rest",
            methods=("GET",),
            path="/widgets",
        ),
    )

    restored = BindingSpec.from_json(spec.to_json())

    assert isinstance(spec, SerdeMixin)
    assert isinstance(restored, BindingSpec)
    assert restored.name == "list_widgets"
    assert isinstance(restored.spec, HttpRestBindingSpec)
    assert restored.spec.path == "/widgets"


def test_binding_registry_spec_inherits_serde_mixin_and_round_trips() -> None:
    binding = BindingSpec(
        name="create_widget",
        spec=HttpRestBindingSpec(
            proto="http.rest",
            methods=("POST",),
            path="/widgets",
        ),
    )
    registry = BindingRegistrySpec()
    registry.register(binding)

    restored = BindingRegistrySpec.from_json(registry.to_json())

    assert isinstance(registry, SerdeMixin)
    assert isinstance(restored, BindingRegistrySpec)
    restored_binding = restored.get("create_widget")
    assert restored_binding is not None
    assert restored_binding.name == "create_widget"
    assert isinstance(restored_binding.spec, HttpRestBindingSpec)
