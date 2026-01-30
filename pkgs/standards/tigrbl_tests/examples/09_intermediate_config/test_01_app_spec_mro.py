"""Lesson 09.1: Understanding app-level configuration precedence."""

from tigrbl import Base, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_spec_mro_prefers_subclass():
    """Explain that app subclasses override scalar configuration fields.

    Purpose: show that child app classes can safely override title/version while
    retaining other defaults.
    Design practice: consolidate defaults in base classes and override sparingly.
    """

    # Setup: define a base app class with defaults.
    class BaseApp(TigrblApp):
        TITLE = "Base"
        VERSION = "1.0.0"
        JSONRPC_PREFIX = "/rpc"

    # Setup: override a scalar value in the child app.
    class ChildApp(BaseApp):
        TITLE = "Child"

    # Deployment: instantiate the child app to materialize settings.
    app = ChildApp()

    # Assertion: the child value takes precedence, while base defaults remain.
    assert app.title == "Child"
    assert app.jsonrpc_prefix == "/rpc"


def test_app_spec_mro_merges_sequence_attributes():
    """Show that app composition favors child-level model declarations.

    Purpose: demonstrate that composing models on the app prefers the child
    declaration, which is a practical precedence rule for app wiring.
    Design practice: declare definitive model lists at the app boundary.
    """

    # Setup: define two minimal models for app composition.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_app_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class Gadget(Base, GUIDPk):
        __tablename__ = "lesson_app_gadget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Setup: base app declares Widget.
    class BaseApp(TigrblApp):
        MODELS = (Widget,)

    # Setup: child app overrides with Gadget for precedence.
    class ChildApp(BaseApp):
        MODELS = (Gadget,)

    # Deployment: instantiate the child app to materialize model registry.
    app = ChildApp()

    # Assertion: the child model list takes precedence at the app boundary.
    assert list(app.models.values()) == [Gadget]
