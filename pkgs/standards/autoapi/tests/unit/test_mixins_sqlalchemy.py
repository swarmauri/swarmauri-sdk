from autoapi.v3.orm.mixins import GUIDPk, Timestamped
from autoapi.v3.table import Base


def test_mixins_define_model_without_error() -> None:
    class MyModel(Base, GUIDPk, Timestamped):
        __tablename__ = "my_models"

    assert {
        "id",
        "created_at",
        "updated_at",
    } <= set(MyModel.__table__.c.keys())
