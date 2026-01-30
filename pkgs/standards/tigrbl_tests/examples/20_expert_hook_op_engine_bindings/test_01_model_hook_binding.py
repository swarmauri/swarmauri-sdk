"""Lesson 20: model hook bindings.

Hooks are attached to model namespaces under ``hooks.<alias>.<PHASE>``,
providing an ordered sequence of callables for each phase. This pattern is
preferred because it keeps hook discovery close to the model definition and
makes ordering explicit.
"""

from tigrbl import Base, bind, hook_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_model_hook_binding_populates_phase_chain():
    """Hook decorators attach callables to the model hook namespace."""

    @hook_ctx(ops="create", phase="POST_COMMIT")
    def notify(cls, ctx):
        return None

    class LessonHookBinding(Base, GUIDPk):
        __tablename__ = "lessonhookbindings"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonHookBinding
    Widget.notify = notify

    bind(Widget)

    hooks = Widget.hooks.create.POST_COMMIT
    assert any(step.__name__ == "notify" for step in hooks)


def test_model_hook_namespace_exposes_phase_lists():
    """The hook namespace should expose a list for each configured phase."""

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def audit(cls, ctx):
        return None

    class LessonHookBindingPhase(Base, GUIDPk):
        __tablename__ = "lessonhookbindingphases"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonHookBindingPhase
    Widget.audit = audit

    bind(Widget)

    assert isinstance(Widget.hooks.create.PRE_HANDLER, list)
