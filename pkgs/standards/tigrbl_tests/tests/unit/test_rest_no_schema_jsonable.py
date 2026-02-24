import pytest
from httpx import ASGITransport, Client
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped

from tigrbl import TigrblApp
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

<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Gadget, prefix="")
    app.initialize()
=======
    router = Tigrblv3(engine=mem(async_=False))
    router.include_model(Gadget, prefix="")
    router.initialize()
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c

    # Remove generated out schemas to exercise jsonable fallback
    Gadget.schemas.read.out = None  # type: ignore[attr-defined]
    Gadget.schemas.list.out = None  # type: ignore[attr-defined]

<<<<<<< HEAD
    transport = ASGITransport(app=app)
=======
    transport = ASGITransport(app=router)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    with Client(transport=transport, base_url="http://test") as client:
        yield client, Gadget


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
