from tigrbl import Base, schema_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.schema import collect_decorated_schemas
from tigrbl.types import BaseModel


def test_schema_ctx_promotes_plain_classes_to_pydantic():
    collect_decorated_schemas.cache_clear()

    class Widget(Base, GUIDPk):
        __tablename__ = "plain_widget"

        @schema_ctx(alias="Ping", kind="in")
        class Ping:
            message: str | None = None
            attempts: int = 1

        @schema_ctx(alias="Ping", kind="out")
        class Pong:
            ok: bool = True

    mapping = collect_decorated_schemas(Widget)
    ping_model = mapping["Ping"]["in"]
    pong_model = mapping["Ping"]["out"]

    assert issubclass(ping_model, BaseModel)
    assert issubclass(pong_model, BaseModel)

    inst = ping_model()
    assert inst.attempts == 1
    assert inst.model_dump() == {"message": None, "attempts": 1}

    out = pong_model()
    assert out.model_dump() == {"ok": True}
