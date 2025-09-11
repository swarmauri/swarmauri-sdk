from tigrbl.column import F, S, acol, vcol
from tigrbl.orm.tables import Base
from tigrbl.types import Integer, Mapped, String
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


def test_acol_vcol_bind_to_table_and_orm() -> None:
    """`acol`/`vcol` integrate with table metadata and ORM instances."""

    Base.metadata.clear()
    engine = create_engine("sqlite:///:memory:")

    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(storage=S(type_=String, nullable=False))
        upper: str = vcol(
            field=F(py_type=str),
            read_producer=lambda obj, ctx: obj.name.upper(),
            nullable=True,
        )

    Base.metadata.create_all(engine)

    # Table contains columns for both persisted and virtual specs
    assert set(User.__table__.c.keys()) == {"id", "name", "upper"}

    # Spec map tracks both persisted and virtual columns
    assert set(User.__tigrbl_cols__.keys()) == {"id", "name", "upper"}
    assert User.__tigrbl_cols__["upper"].storage is None

    with Session(engine) as session:
        user = User(name="Alice")
        session.add(user)
        session.commit()
        session.refresh(user)

        # persisted column round-trips through the DB
        result = session.execute(select(User.name)).scalar_one()
        assert result == "Alice"

        # DB column for virtual spec defaults to NULL
        raw = session.execute(select(User.upper)).scalar_one()
        assert raw is None

        # virtual column value produced dynamically
        spec = User.__tigrbl_cols__["upper"]
        assert spec.read_producer(user, {}) == "ALICE"
