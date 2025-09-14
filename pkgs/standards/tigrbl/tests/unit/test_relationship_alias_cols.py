import pytest
from tigrbl.specs import F, S, acol, vcol
from tigrbl.op import alias_ctx
from tigrbl.orm.tables import Base
from tigrbl.deps import (
    Column,
    Integer,
    String,
    ForeignKey,
    relationship,
    Mapped,
    create_engine,
    Session,
)


@pytest.mark.parametrize("col_variant", ["acol", "vcol", "both"])
@pytest.mark.parametrize("aliasing", [False, True])
@pytest.mark.parametrize("use_mapped", [False, True])
def test_relationship_acol_vcol_alias(col_variant, aliasing, use_mapped):
    Base.metadata.clear()
    Base.registry.dispose()
    engine = create_engine("sqlite:///:memory:")

    decorator = alias_ctx(read="fetch") if aliasing else (lambda cls: cls)

    if use_mapped:

        @decorator
        class Parent(Base):
            __tablename__ = f"p_{col_variant}_{aliasing}_{use_mapped}"
            id: Mapped[int] = Column(Integer, primary_key=True)
            if col_variant in ("acol", "both"):
                name: Mapped[str] = acol(storage=S(type_=String, nullable=True))
            if col_variant in ("vcol", "both"):
                nickname: str = vcol(
                    field=F(py_type=str),
                    read_producer=lambda obj, ctx: "nick",
                    nullable=True,
                )
            children: Mapped[list["Child"]] = relationship(back_populates="parent")

        @decorator
        class Child(Base):
            __tablename__ = f"c_{col_variant}_{aliasing}_{use_mapped}"
            id: Mapped[int] = Column(Integer, primary_key=True)
            parent_id: Mapped[int] = Column(
                Integer, ForeignKey(f"{Parent.__tablename__}.id")
            )
            if col_variant in ("acol", "both"):
                name: Mapped[str] = acol(storage=S(type_=String, nullable=True))
            if col_variant in ("vcol", "both"):
                nickname: str = vcol(
                    field=F(py_type=str),
                    read_producer=lambda obj, ctx: "nick",
                    nullable=True,
                )
            parent: Mapped["Parent"] = relationship(back_populates="children")
    else:

        @decorator
        class Parent(Base):
            __tablename__ = f"p_{col_variant}_{aliasing}_{use_mapped}"
            id = Column(Integer, primary_key=True)
            if col_variant in ("acol", "both"):
                name: str = acol(storage=S(type_=String, nullable=True))
            if col_variant in ("vcol", "both"):
                nickname: str = vcol(
                    field=F(py_type=str),
                    read_producer=lambda obj, ctx: "nick",
                    nullable=True,
                )
            children = relationship("Child", back_populates="parent")

        @decorator
        class Child(Base):
            __tablename__ = f"c_{col_variant}_{aliasing}_{use_mapped}"
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey(f"{Parent.__tablename__}.id"))
            if col_variant in ("acol", "both"):
                name: str = acol(storage=S(type_=String, nullable=True))
            if col_variant in ("vcol", "both"):
                nickname: str = vcol(
                    field=F(py_type=str),
                    read_producer=lambda obj, ctx: "nick",
                    nullable=True,
                )
            parent = relationship("Parent", back_populates="children")

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        p = Parent()
        c = Child(parent=p)
        session.add_all([p, c])
        session.commit()
        session.refresh(p)
        assert c.parent is p
        assert p.children[0] is c
