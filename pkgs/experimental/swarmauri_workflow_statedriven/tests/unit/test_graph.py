# File: tests/workflows/test_graph.py

import pytest
from graphviz import Digraph
from swarmauri_workflow_statedriven.graph import WorkflowGraph
from swarmauri_workflow_statedriven.conditions.function_condition import FunctionCondition

class DummyAgent:
    """
    Simple agent stub with exec(input) -> f"{input}_out"
    """
    def exec(self, input_data):
        return f"{input_data}_out"

def test_execute_returns_expected_results():
    """
    Test WorkflowGraph.execute produces correct outputs for a simple two‑state workflow.
    (File: workflows/graph.py → class WorkflowGraph → method execute)
    """
    wf = WorkflowGraph()
    a_agent = DummyAgent()
    b_agent = DummyAgent()
    wf.add_state("A", agent=a_agent)
    wf.add_state("B", agent=b_agent)
    wf.add_transition("A", "B", FunctionCondition(lambda s: True))

    results = wf.execute("A", "start")
    # A.exec appends "_out"
    assert results["A"] == "start_out"
    # B.exec receives "start_out" and appends another "_out"
    assert results["B"] == "start_out_out"

def test_visualize_contains_nodes_and_edges(tmp_path):
    """
    Test WorkflowGraph.visualize returns a Digraph with the correct nodes and edge labels.
    (File: workflows/graph.py → class WorkflowGraph → method visualize)
    """
    wf = WorkflowGraph()
    wf.add_state("X", agent=DummyAgent())
    wf.add_state("Y", agent=DummyAgent())
    wf.add_transition("X", "Y", FunctionCondition(lambda s: True))

    dot: Digraph = wf.visualize()
    assert isinstance(dot, Digraph)

    src = dot.source
    # should list both nodes
    assert "X" in src
    assert "Y" in src
    # should include the edge and the condition label
    assert "X -> Y" in src
    assert "FunctionCondition" in src

    # test rendering to file
    out_file = tmp_path / "workflow_graph"
    rendered = wf.visualize(str(out_file))
    assert out_file.with_suffix(".gv").exists() or out_file.with_suffix(".gv").is_file()
    assert isinstance(rendered, Digraph)
