from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.app_spec import AppSpec
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


class ConcreteColumnSpec(SerdeMixin, ColumnSpec):
    def __init__(
        self,
        *,
        storage: StorageSpec | None,
        field: FieldSpec | None = None,
        io: IOSpec | None = None,
        default_factory: Any = None,
        read_producer: Any = None,
    ) -> None:
        self.storage = storage
        self.field = field if field is not None else FieldSpec()
        self.io = io if io is not None else IOSpec()
        self.default_factory = default_factory
        self.read_producer = read_producer

    @property
    def storage(self) -> StorageSpec | None:
        return self.__dict__["storage"]

    @storage.setter
    def storage(self, value: StorageSpec | None) -> None:
        self.__dict__["storage"] = value

    @property
    def field(self) -> FieldSpec:
        return self.__dict__["field"]

    @field.setter
    def field(self, value: FieldSpec) -> None:
        self.__dict__["field"] = value

    @property
    def io(self) -> IOSpec:
        return self.__dict__["io"]

    @io.setter
    def io(self, value: IOSpec) -> None:
        self.__dict__["io"] = value

    @property
    def default_factory(self) -> Any:
        return self.__dict__["default_factory"]

    @default_factory.setter
    def default_factory(self, value: Any) -> None:
        self.__dict__["default_factory"] = value

    @property
    def read_producer(self) -> Any:
        return self.__dict__["read_producer"]

    @read_producer.setter
    def read_producer(self, value: Any) -> None:
        self.__dict__["read_producer"] = value


def test_column_spec_json_round_trip_restores_nested_specs() -> None:
    spec = ConcreteColumnSpec(
        storage=StorageSpec(
            type_=ExampleClass,
            nullable=False,
            fk=ForeignKeySpec(target="widgets.id", on_delete="CASCADE"),
        ),
        field=FieldSpec(py_type=str, constraints={"max_length": 50}),
        io=IOSpec(in_verbs=("create",), out_verbs=("read",)),
    )

    restored = ConcreteColumnSpec.from_json(spec.to_json())

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
    spec = ConcreteColumnSpec(
        storage=StorageSpec(
            type_=str,
            nullable=True,
            fk=ForeignKeySpec(target="parents.id"),
        ),
        field=FieldSpec(py_type=str),
        io=IOSpec(out_verbs=("list",)),
    )

    restored = ConcreteColumnSpec.from_yaml(spec.to_yaml())

    assert restored.storage is not None
    assert restored.storage.fk is not None
    assert restored.storage.fk.target == "parents.id"
    assert restored.io.out_verbs == ("list",)
