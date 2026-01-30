from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Integer, Mapped, String


def test_mapped_mixins_extend_base_model():
    """Show mapped mixins compose cleanly with base classes.

    Purpose:
        Validate that a mixin-provided primary key (``GUIDPk``) and a mapped
        attribute can coexist without conflicting configuration.

    What this shows:
        - Mixins contribute columns to the final table.
        - ``mapped_column`` defaults are retained in the table metadata.

    Best practice:
        Keep shared concerns (IDs, timestamps) in mixins and feature-specific
        fields in the model body for clean composition.
    """

    # Setup: mix in GUIDPk and add a typed Column for a rating field.
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_mixins"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        rating: Mapped[int] = Column(Integer, default=5)

    # Deployment: not required; column defaults are on the class metadata.
    # Test: inspect SQLAlchemy's column default for the mixin-backed model.
    column_default = Widget.__table__.c.rating.default
    # Assertion: the default value survives declarative mapping.
    assert column_default is not None
    assert column_default.arg == 5


def test_mixin_primary_key_is_materialized():
    """Confirm that mixin-provided primary keys are present on the table.

    Purpose:
        Ensure ``GUIDPk`` contributes the identifier column alongside custom
        mapped attributes.

    What this shows:
        - Mixins are first-class participants in table creation.
        - The model still retains explicit, readable field declarations.

    Best practice:
        Centralize identifier conventions via mixins to keep models consistent.
    """

    # Setup: define a model that uses the GUIDPk mixin.
    class Widget(Base, GUIDPk):
        __tablename__ = "mapped_mixin_pk"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)
        rating: Mapped[int] = Column(Integer, default=1)

    # Deployment: not required; the primary key is on the class metadata.
    # Assertion: the primary key column contributed by the mixin is present.
    assert "id" in Widget.__table__.c
    assert Widget.__table__.c.id.primary_key is True
