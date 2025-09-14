import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped

from tigrbl import TigrblApp as Tigrblv3
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import F, IO, S, acol
from tigrbl.orm.tables import Base as Base3


@pytest.fixture()
def client_and_model():
    Base3.metadata.clear()

    class Gadget(Base3):
        __tablename__ = "gadgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )
        age: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=0),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )

        __tigrbl_cols__ = {"id": id, "name": name, "age": age}

    api = Tigrblv3(engine=mem(async_=False))
    api.include_model(Gadget, prefix="")
    api.initialize()

    # Remove generated out schemas to exercise jsonable fallback
    Gadget.schemas.read.out = None  # type: ignore[attr-defined]
    Gadget.schemas.list.out = None  # type: ignore[attr-defined]

    client = TestClient(api)
    try:
        yield client, Gadget
    finally:
        client.close()


def test_rest_read_and_list_without_schema(client_and_model):
    client, _ = client_and_model
    created = client.post("/gadget", json={"name": "A", "age": 1})
    item_id = created.json()["id"]

    resp = client.get(f"/gadget/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id

    resp_list = client.get("/gadget")
    assert resp_list.status_code == 200
    ids = {item["id"] for item in resp_list.json()}
    assert item_id in ids
