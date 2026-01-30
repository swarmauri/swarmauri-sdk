from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_model_instantiation_sets_attributes():
    """Confirm constructor arguments populate model attributes.

    Purpose: show that declarative models behave like normal Python objects,
    making them easy to instantiate in unit tests or seed data workflows.
    This reinforces that model state is immediately accessible without
    persisting to the database.

    Best practice: initialize required fields explicitly so the object is
    always in a valid state before persistence or serialization.
    """

    # Setup: define a simple widget model with one required column.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessoninstances"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: instantiate a model instance in memory.
    widget = Widget(name="starter")
    # Exercise: access the field on the instance.
    assert widget.name == "starter"


def test_multiple_instances_keep_independent_state():
    """Illustrate that each model instance owns its own data.

    Purpose: demonstrate that independent objects can be created from the same
    model class without leaking values between them.

    Best practice: create separate instances for each record in tests to avoid
    stateful coupling and to mimic real-world request lifecycles.
    """

    # Setup: reuse the same model definition for multiple instances.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonmultiinstances"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    # Deployment: create two independent instances.
    first = Widget(name="alpha")
    second = Widget(name="beta")

    # Assertion: verify each instance retains its own data.
    assert first.name == "alpha"
    assert second.name == "beta"
