from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, String


def test_nonmapped_columns_use_column_instances():
    """Explain non-mapped columns as explicit ``Column`` declarations.

    Purpose:
        Show that non-mapped fields can still be defined with SQLAlchemy
        ``Column`` objects when you opt out of typed ``Mapped`` annotations.

    What this shows:
        - Plain ``Column`` attributes are collected into ``__table__``.
        - ``__allow_unmapped__`` enables mixed typed/untyped definitions.

    Best practice:
        Use plain ``Column`` when you are integrating legacy models or need
        minimal typing overhead, but remain explicit about nullability.
    """

    # Setup: define a model that uses explicit Column instances only.
    class Widget(Base, GUIDPk):
        __tablename__ = "nonmapped_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        priority = Column(Integer, default=1)

    # Deployment: not required; the model metadata is already built.
    # Assertion: SQLAlchemy still collects the non-mapped column.
    assert "priority" in Widget.__table__.c


def test_nonmapped_column_defaults_and_nullability():
    """Reinforce that explicit columns keep defaults and nullability visible.

    Purpose:
        Confirm that non-mapped ``Column`` definitions preserve defaults and
        nullability flags on the final table metadata.

    What this shows:
        - Defaults are attached to SQLAlchemy columns.
        - ``nullable`` is enforced at the schema layer.

    Best practice:
        Keep these settings close to the model to avoid drift between intent
        and the generated table definition.
    """

    # Setup: define defaults and nullability directly on the Column.
    class Widget(Base, GUIDPk):
        __tablename__ = "nonmapped_defaults"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        priority = Column(Integer, default=2, nullable=False)

    # Deployment: not required; inspect the table metadata directly.
    # Test: inspect the table metadata for default/nullability.
    column = Widget.__table__.c.priority
    # Assertion: default and nullability are preserved on the schema.
    assert column.default is not None
    assert column.default.arg == 2
    assert column.nullable is False
