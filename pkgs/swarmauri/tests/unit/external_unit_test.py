import os
from unittest.mock import MagicMock, patch

import pytest

from swarmauri.external import call_external_llm, call_external_agent


@pytest.fixture(autouse=True)
def clear_env():
    old = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old)


@pytest.mark.unit
def test_call_external_llm_basic():
    with patch(
        "swarmauri.external.PluginCitizenshipRegistry.get_external_module_path",
        return_value="swarmauri.tests.unit.dummy_module",
    ) as mock_get, patch("importlib.import_module") as mock_import:
        module = MagicMock()
        module.DummyLLM = MagicMock()
        mock_import.return_value = module

        call_external_llm("DummyLLM", api_key="k", model_name="m")

        mock_get.assert_called_once_with("swarmauri.llms.DummyLLM")
        module.DummyLLM.assert_called_once_with(api_key="k", name="m", timeout=1200.0)


@pytest.mark.unit
def test_call_external_agent_basic():
    dummy_llm = MagicMock()
    dummy_agent_cls = MagicMock()
    dummy_agent = MagicMock()
    dummy_agent_cls.return_value = dummy_agent
    dummy_agent.conversation = MagicMock()
    dummy_agent.exec.return_value = "result"

    with (
        patch("swarmauri.external.call_external_llm", return_value=dummy_llm),
        patch(
            "swarmauri.external._load_registered_class",
            return_value=dummy_agent_cls,
        ),
        patch("swarmauri.external.chunk_content", side_effect=lambda x, logger=None: x),
    ):
        env = {"provider": "DummyLLM", "agent_class": "DummyAgent", "max_tokens": 10}
        result = call_external_agent("hi", env)

    assert result == "result"
    dummy_agent_cls.assert_called_once_with(llm=dummy_llm)
    dummy_agent.exec.assert_called_once_with("hi", llm_kwargs={"max_tokens": 10})
