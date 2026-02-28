from tigrbl import TableBase
from tigrbl.orm.mixins import GUIDPk, Timestamped


def test_mixins_define_model_without_error() -> None:
    class MyModel(TableBase, GUIDPk, Timestamped):
        __tablename__ = "my_models"

    assert {
        "id",
        "created_at",
        "updated_at",
    } <= set(MyModel.__table__.c.keys())
