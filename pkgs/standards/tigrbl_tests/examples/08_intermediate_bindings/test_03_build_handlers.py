"""Lesson 08.3: Building handler pipelines."""

from tigrbl import Base, bind, build_handlers
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_build_handlers_returns_handlers():
    """Explain that handler builders attach per-op handler pipelines.

    Purpose: show that the handlers namespace is populated after binding.
    Design practice: inspect handlers when debugging execution flow.
    """

    # Setup: define a model with a required column.
    class LessonHandlers(Base, GUIDPk):
        __tablename__ = "lesson_handlers"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind the model and build handlers.
    specs = bind(LessonHandlers)
    build_handlers(LessonHandlers, specs)

    # Assertion: the handlers namespace is created.
    assert hasattr(LessonHandlers, "handlers")


def test_build_handlers_creates_list_handler():
    """Confirm that a canonical op gets a handler entrypoint.

    Purpose: verify that the list operation has a handler namespace so it can be
    invoked consistently.
    Design practice: rely on handler namespaces to keep invocation uniform.
    """

    # Setup: define another model for handler inspection.
    class LessonHandlersList(Base, GUIDPk):
        __tablename__ = "lesson_handlers_list"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind and build handlers for the model.
    specs = bind(LessonHandlersList)
    build_handlers(LessonHandlersList, specs)

    # Test: verify handler namespace for the list operation.
    assert hasattr(LessonHandlersList.handlers, "list")
