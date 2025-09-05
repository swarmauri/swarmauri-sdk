import pytest
from swarmauri_core.agents.IAgent import IAgent


@pytest.mark.unit
def test_iagent_methods_are_abstract():
    for name in ["exec", "aexec", "batch", "abatch"]:
        assert hasattr(IAgent, name)
        method = getattr(IAgent, name)
        assert getattr(method, "__isabstractmethod__", False)
