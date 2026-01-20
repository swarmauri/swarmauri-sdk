from fastapi import FastAPI

from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base


class Item(Base, GUIDPk):
    __tablename__ = "items_operation_id"


def _collect_operation_ids(schema: dict) -> list[str]:
    ids: list[str] = []
    for path in schema["paths"].values():
        for method in path.values():
            operation_id = method.get("operationId")
            if operation_id:
                ids.append(operation_id)
    return ids


def test_operation_ids_are_unique():
    Base.metadata.clear()
    router = _build_router(
        Item,
        [
            OpSpec(alias="dup", target="custom", arity="collection"),
            OpSpec(alias="dup", target="custom", arity="member"),
        ],
    )
    app = FastAPI()
    app.include_router(router)
    schema = app.openapi()
    operation_ids = _collect_operation_ids(schema)
    assert len(operation_ids) == len(set(operation_ids))
