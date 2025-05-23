# File: tests/workflows/test_graph.py

import pytest
from swarmauri_workflow_statedriven.graph import WorkflowGraph
from swarmauri_workflow_statedriven.conditions.function_condition import (
    FunctionCondition,
)


class DummyAgent:
    """
    Simple agent stub with exec(input) -> f"{input}_out"
    """

    def exec(self, input_data):
        return f"{input_data}_out"


@pytest.mark.unit
def test_execute_returns_expected_results():
    """
    File: workflows/graph.py
    Class: WorkflowGraph
    Method: execute

    Test that execute runs a simple two‑state workflow correctly.
    """
    wf = WorkflowGraph()
    a_agent = DummyAgent()
    b_agent = DummyAgent()
    wf.add_state("A", agent=a_agent)
    wf.add_state("B", agent=b_agent)

    def always_true(_state):
        return True

    wf.add_transition("A", "B", FunctionCondition(always_true))

    results = wf.execute("A", "start")
    assert results["A"] == "start_out"
    assert results["B"] == "start_out_out"


@pytest.mark.unit
def test_visualize_returns_dot_string_and_contains_nodes_edges(tmp_path):
    """
    File: workflows/graph.py
    Class: WorkflowGraph
    Method: visualize

    visualize() should return a DOT string with node and edge definitions.
    """
    wf = WorkflowGraph()
    wf.add_state("X", agent=DummyAgent())
    wf.add_state("Y", agent=DummyAgent())

    def always_true(_state):
        return True

    wf.add_transition("X", "Y", FunctionCondition(always_true))

    dot = wf.visualize()
    # Return type is str (DOT source)
    assert isinstance(dot, str)
    # Should include graph declaration
    assert dot.startswith("flowchart TD")
    # Should list both nodes
    assert '"X";' in dot
    assert '"Y";' in dot
    # Should include the edge with condition label
    assert '"X" -> "Y" [label="FunctionCondition"];' in dot

    # Now test writing to file
    basename = tmp_path / "my_workflow"
    dot2 = wf.visualize(str(basename))
    # Should still return the same content
    assert dot2 == dot
    dot_file = basename.with_suffix(".dot")
    assert dot_file.exists()
    content = dot_file.read_text(encoding="utf-8")
    assert content == dot


@pytest.mark.skip(reason="Requires headless browser environment")
def test_visualize_png_headless_creates_png(tmp_path):
    """
    File: workflows/graph.py
    Class: WorkflowGraph
    Method: visualize_png_headless

    This test is skipped by default because it requires pyppeteer and a headless browser.
    """
    wf = WorkflowGraph()
    wf.add_state("A", agent=DummyAgent())
    wf.add_state("B", agent=DummyAgent())

    def always_true(_state):
        return True

    wf.add_transition("A", "B", FunctionCondition(always_true))

    png_path = tmp_path / "graph.png"
    result_path = wf.visualize_png_headless(str(png_path))
    assert result_path == str(png_path)
    assert png_path.exists()
    # Optionally, check file size > 0
    assert png_path.stat().st_size > 0
