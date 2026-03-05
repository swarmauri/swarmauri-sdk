from tigrbl.orm.tables.user import User


def test_user_table_name() -> None:
    assert User.__tablename__ == "users"
