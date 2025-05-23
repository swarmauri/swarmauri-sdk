# File: tests/workflows/test_node.py

import pytest
from swarmauri_workflow_statedriven.node import Node
from swarmauri_workflow_statedriven.input_modes.first import FirstInputMode
from swarmauri_workflow_statedriven.input_modes.identity import IdentityInputMode
from swarmauri_workflow_statedriven.input_modes.base import InputMode


class DummyAgent:
    """
    Stub agent with exec() and batch().
    """

    def __init__(self):
        self.calls = []

    def exec(self, data):
        self.calls.append(data)
        return f"A:{data}"

    def batch(self, data_list):
        self.calls.append(tuple(data_list))
        return [f"A:{item}" for item in data_list]


class DummyTool:
    """
    Stub tool with run() and batch().
    """

    def __init__(self):
        self.calls = []

    def call(self, data):
        self.calls.append(data)
        return f"T:{data}"

    def batch(self, data_list):
        self.calls.append(tuple(data_list))
        return [f"T:{item}" for item in data_list]


class EchoInputMode(InputMode):
    """
    InputMode that prefixes incoming data with 'prep:'.
    """

    def prepare(self, state_manager, node_name, data, results):
        return f"prep:{data}"


@pytest.mark.unit
def test_init_requires_exactly_one_backend():
    """
    File: workflows/node.py
    Class: Node
    Method: __init__
    """
    # neither agent nor tool
    with pytest.raises(ValueError):
        Node("n1", input_mode=FirstInputMode())
    # both agent and tool
    with pytest.raises(ValueError):
        Node("n2", agent=DummyAgent(), tool=DummyTool(), input_mode=FirstInputMode())


@pytest.mark.unit
def test_execute_delegates_to_agent_or_tool():
    """
    File: workflows/node.py
    Class: Node
    Method: execute
    """
    agent = DummyAgent()
    node_a = Node("nA", agent=agent, input_mode=FirstInputMode())
    assert node_a.execute("foo") == "A:foo"
    assert agent.calls == ["foo"]

    tool = DummyTool()
    node_t = Node("nT", tool=tool, input_mode=FirstInputMode())
    assert node_t.execute("bar") == "T:bar"
    assert tool.calls == ["bar"]


@pytest.mark.unit
def test_batch_uses_batch_or_fallback():
    """
    File: workflows/node.py
    Class: Node
    Method: batch
    """
    # agent with batch()
    agent = DummyAgent()
    node_a = Node("nA", agent=agent, input_mode=FirstInputMode())
    out = node_a.batch(["x", "y"])
    assert out == ["A:x", "A:y"]
    assert agent.calls == [("x", "y")]

    # agent without batch() falls back to exec()
    class NoBatchAgent:
        def __init__(self):
            self.calls = []

        def exec(self, data):
            self.calls.append(data)
            return data.upper()

    nb_agent = NoBatchAgent()
    node_nb = Node("nNB", agent=nb_agent, input_mode=FirstInputMode())
    out2 = node_nb.batch(["a", "b"])
    assert out2 == ["A", "B"]  # "a".upper() -> "A", etc.
    assert nb_agent.calls == ["a", "b"]


@pytest.mark.unit
def test_prepare_input_applies_input_mode():
    """
    File: workflows/node.py
    Class: Node
    Method: prepare_input
    """
    agent = DummyAgent()
    mode = EchoInputMode()
    node = Node("nE", agent=agent, input_mode=mode)
    # 'prepare' should prefix data
    prepared = node.prepare_input(state_manager=None, data="data", results={})
    assert prepared == "prep:data"


@pytest.mark.unit
def test_run_dispatches_execute_and_batch():
    """
    File: workflows/node.py
    Class: Node
    Method: run
    """

    # scalar path with custom input_mode
    class PassAgent:
        def exec(self, x):
            return f"exec:{x}"

    node1 = Node("n1", agent=PassAgent(), input_mode=EchoInputMode())

    class DummySM:
        def update_state(self, *a, **k):
            pass

        def buffer_input(self, *a, **k):
            pass

        def get_buffer(self, *a, **k):
            return []

        def pop_buffer(self, *a, **k):
            return []

    sm = DummySM()
    results = {}
    out1 = node1.run(sm, "orig", results)
    assert out1 == "exec:prep:orig"

    # batch path
    class BatchAgent:
        def exec(self, x):
            raise AssertionError("should not use exec")

        def batch(self, xs):
            return [f"b:{i}" for i in xs]

    node2 = Node("n2", agent=BatchAgent(), input_mode=IdentityInputMode())
    out2 = node2.run(sm, ["p", "q"], results)
    assert out2 == ["b:p", "b:q"]


@pytest.mark.unit
def test_validate_default_returns_true():
    """
    File: workflows/node.py
    Class: Node
    Method: validate
    """
    node = Node("nV", agent=DummyAgent(), input_mode=FirstInputMode())
    assert node.validate("anything") is True
