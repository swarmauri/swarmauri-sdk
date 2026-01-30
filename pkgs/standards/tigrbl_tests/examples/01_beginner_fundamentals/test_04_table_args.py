from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import CheckConstraint, Column, String, UniqueConstraint


def test_table_args_register_constraints():
    """Ensure ``__table_args__`` constraints reach table metadata.

    Purpose: reinforce how table-level constraints are registered when the
    model class is created, giving immediate feedback on schema rules.

    Best practice: declare constraints close to the model to keep validation
    rules and business intent discoverable.
    """
    # Setup: define table-level constraints explicitly.
    constraints = (
        UniqueConstraint("name", name="uq_widget_name"),
        CheckConstraint("length(name) > 0", name="ck_widget_name"),
    )

    class Widget(Base, GUIDPk):
        __tablename__ = "lessonconstraints"
        __allow_unmapped__ = True
        __table_args__ = constraints
        name = Column(String, nullable=False)

    # Deployment: the constraints are attached during class creation.
    constraint_names = {constraint.name for constraint in Widget.__table__.constraints}
    # Assertion: ensure both constraints are registered in metadata.
    assert "uq_widget_name" in constraint_names
    assert "ck_widget_name" in constraint_names


def test_table_args_are_exposed_on_the_model_class():
    """Demonstrate that table args remain attached to the model class.

    Purpose: show that ``__table_args__`` can be inspected without diving into
    the table object, which is helpful for metaprogramming or documentation.

    Best practice: keep table args deterministic so tooling can reliably
    parse and document constraints.
    """
    # Setup: declare constraints alongside the model.
    constraints = (
        UniqueConstraint("name", name="uq_widget_name"),
        CheckConstraint("length(name) > 0", name="ck_widget_name"),
    )

    class Widget(Base, GUIDPk):
        __tablename__ = "lessonconstraintsreview"
        __allow_unmapped__ = True
        __table_args__ = constraints
        name = Column(String, nullable=False)

    # Deployment: inspect the class-level ``__table_args__`` tuple directly.
    table_args = Widget.__table_args__
    constraint_names = {constraint.name for constraint in table_args}
    # Assertion: confirm constraint names match expectations.
    assert {"uq_widget_name", "ck_widget_name"}.issubset(constraint_names)
