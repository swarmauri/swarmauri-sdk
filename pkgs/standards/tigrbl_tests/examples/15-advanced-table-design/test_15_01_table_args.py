from __future__ import annotations

from tigrbl import Base
from tigrbl.types import CheckConstraint, Index, UniqueConstraint


def test_table_args_multiple_constraints() -> None:
    class Catalog(Base):
        __tablename__ = "catalogs"
        __table_args__ = (
            UniqueConstraint("slug", name="uq_catalog_slug"),
            CheckConstraint("quantity >= 0", name="ck_catalog_quantity"),
            Index("ix_catalog_slug", "slug"),
        )

    constraints = Catalog.__table_args__
    assert any(isinstance(item, UniqueConstraint) for item in constraints)
    assert any(isinstance(item, CheckConstraint) for item in constraints)
    assert any(isinstance(item, Index) for item in constraints)
