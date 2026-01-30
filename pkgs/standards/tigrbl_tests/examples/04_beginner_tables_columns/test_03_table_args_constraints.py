from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import CheckConstraint, Column, String, UniqueConstraint


def test_table_constraints_are_in_metadata():
    """Ensure constraints appear in table metadata.

    Purpose: show that model-level constraints populate the table object, so
    schema inspection tools can see them immediately.

    Best practice: validate constraints at the model level to surface issues
    before deployment or migrations.
    """
    # Setup: attach table-level constraints directly on the model.
    constraints = (
        UniqueConstraint("name", name="uq_widget_name"),
        CheckConstraint("length(name) > 0", name="ck_widget_name"),
    )

    class Widget(Base, GUIDPk):
        __tablename__ = "lessontableargs"
        __allow_unmapped__ = True
        __table_args__ = constraints
        name = Column(String, nullable=False)

    # Deployment: table constraints are registered on class creation.
    constraint_names = {constraint.name for constraint in Widget.__table__.constraints}
    # Assertion: the check constraint appears in metadata.
    assert "ck_widget_name" in constraint_names


def test_table_constraints_include_unique_checks():
    """Teach how to verify a unique constraint is present.

    Purpose: confirm that uniqueness rules are attached to the table and can
    be discovered programmatically.

    Best practice: encode uniqueness at the database level for authoritative
    enforcement, even when APIs validate on input.
    """
    # Setup: define another constrained model to isolate unique constraints.
    constraints = (
        UniqueConstraint("name", name="uq_widget_name"),
        CheckConstraint("length(name) > 0", name="ck_widget_name"),
    )

    class Widget(Base, GUIDPk):
        __tablename__ = "lessontableargsunique"
        __allow_unmapped__ = True
        __table_args__ = constraints
        name = Column(String, nullable=False)

    # Deployment: scan table constraints for uniqueness rules.
    unique_constraints = [
        constraint
        for constraint in Widget.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    # Assertion: at least one unique constraint is present.
    assert unique_constraints
