# File: swarmauri/workflows/graph.py

from typing import Any, Dict, Optional
from graphviz import Digraph

from swarmauri_workflow_statedriven.base import WorkflowBase

class WorkflowGraph(WorkflowBase):
    """
    An executable workflow graph with visualization support.
    """

    def __init__(self):
        """
        Initialize an empty WorkflowGraph.
        """
        super().__init__()

    def execute(self, start: str, initial_input: Any) -> Dict[str, Any]:
        """
        Execute the workflow from the given start state.

        Args:
            start: name of the initial state
            initial_input: data to feed into the start state

        Returns:
            A dict mapping each state name to its output.
        """
        return self.run(start, initial_input)

    def visualize(self, filename: Optional[str] = None) -> Digraph:
        """
        Build and optionally save a Graphviz Digraph of the workflow.

        Args:
            filename: If provided, render and save to this path (no extension).

        Returns:
            A graphviz.Digraph representing the workflow structure.
        """
        dot = Digraph(comment="Workflow")
        # Add nodes
        for name in self.nodes:
            dot.node(name)
        # Add edges with condition labels
        for t in self.transitions:
            label = type(t.condition).__name__
            dot.edge(t.source, t.target, label=label)
        # Render to file if requested
        if filename:
            dot.render(filename, cleanup=True)
        return dot
