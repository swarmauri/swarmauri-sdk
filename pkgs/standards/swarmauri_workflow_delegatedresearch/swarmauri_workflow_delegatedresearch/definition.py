"""Reuse the existing workflow's nodes and guarded transitions."""

from swarmauri_workflow_statedriven.base import WorkflowBase
from swarmauri_workflow_statedriven.conditions.base import Condition


class Always(Condition):
    """Follow a successful coordinator transition."""

    def evaluate(self, state):
        return True


class PassThrough:
    """Provide the local coordinator node's ordinary tool behavior."""

    def call(self, value):
        return value


def research_graph():
    """Keep remote child execution inside the authorized dispatcher."""
    graph = WorkflowBase()
    graph.add_state("coordinator", tool=PassThrough())
    graph.add_state("research", tool=PassThrough())
    graph.add_transition("coordinator", "research", Always())
    return graph
