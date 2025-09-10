from tigrbl.specs import S
from tigrbl.column.storage_spec import StorageTransform, ForeignKeySpec
from sqlalchemy import Integer, text


def test_type_attribute() -> None:
    spec = S(type_=Integer)
    assert spec.type_ is Integer


def test_nullable_attribute() -> None:
    spec = S(nullable=False)
    assert spec.nullable is False


def test_unique_attribute() -> None:
    spec = S(unique=True)
    assert spec.unique is True


def test_index_attribute() -> None:
    spec = S(index=True)
    assert spec.index is True


def test_primary_key_attribute() -> None:
    spec = S(primary_key=True)
    assert spec.primary_key is True


def test_autoincrement_attribute() -> None:
    spec = S(autoincrement=True)
    assert spec.autoincrement is True


def test_default_attribute() -> None:
    spec = S(default=1)
    assert spec.default == 1


def test_onupdate_attribute() -> None:
    spec = S(onupdate=lambda: 2)
    assert spec.onupdate() == 2


def test_server_default_attribute() -> None:
    spec = S(server_default=text("NOW()"))
    assert str(spec.server_default) == str(text("NOW()"))


def test_refresh_on_return_attribute() -> None:
    spec = S(refresh_on_return=True)
    assert spec.refresh_on_return is True


def test_transform_attribute() -> None:
    transform = StorageTransform(
        to_stored=lambda v, _ctx: v,
        from_stored=lambda v, _ctx: v,
    )
    spec = S(transform=transform)
    assert spec.transform == transform


def test_fk_attribute() -> None:
    fk = ForeignKeySpec(target="tenant(id)", on_delete="CASCADE")
    spec = S(fk=fk)
    assert spec.fk == fk


def test_check_attribute() -> None:
    spec = S(check="value > 0")
    assert spec.check == "value > 0"


def test_comment_attribute() -> None:
    spec = S(comment="user id")
    assert spec.comment == "user id"
