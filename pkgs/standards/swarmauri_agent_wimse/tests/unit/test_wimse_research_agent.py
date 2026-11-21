"""Exercise the agent and request-bound tool without reference peers."""

from importlib import import_module
from importlib.metadata import entry_points

import pytest
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri_standard.toolkits.Toolkit import Toolkit

from swarmauri_agent_wimse import WimseFileTool, WimseResearchAgent
from swarmauri_agent_wimse.proof import Rejected


@pytest.mark.unit
@pytest.mark.parametrize("requested_file", ["Q3.pdf", "other.pdf"])
def test_agent_dispatches_only_the_authorized_file(
    monkeypatch, requested_file
):
    file_tool_module = import_module("swarmauri_agent_wimse.WimseFileTool")
    proofs, requests = [], []

    def produce_proof(wit, token, **kwargs):
        proofs.append((wit, token))
        return {"Txn-Token": token}

    def post_json(url, body, headers):
        requests.append((url, body, headers))
        return {"file": "Q3.pdf", "content": "$10M", "txn": "transaction"}

    monkeypatch.setattr(file_tool_module, "produce_wpt", produce_proof)
    url = "http://127.0.0.1:5063/files/read"
    tool = WimseFileTool.for_transaction(
        file="Q3.pdf",
        transaction_id="transaction",
        wit="workload-token",
        token="delegated-token",
        audience="file-service",
        signer=object(),
        key_reference="key",
        url=url,
        post_json=post_json,
    )

    def predict(self, *, conversation, toolkit, **kwargs):
        assert isinstance(toolkit, ToolkitBase)
        read_file = toolkit.get_tool_by_name("read_file")
        content = read_file(file=requested_file)
        assert read_file(file=requested_file) == content
        conversation.add_message(AgentMessage(content=content))
        return conversation

    monkeypatch.setattr(OpenAIToolModel, "predict", predict)
    agent = WimseResearchAgent(
        llm=OpenAIToolModel(api_key="unused", name="gpt-4o-mini"),
        toolkit=Toolkit(tools={tool.name: tool}),
    )
    if requested_file == "Q3.pdf":
        assert agent.research("Q3.pdf") == "$10M"
        assert tool.has_read
        assert proofs == [("workload-token", "delegated-token")]
        assert requests == [
            (url, {"file": "Q3.pdf"}, {"Txn-Token": "delegated-token"})
        ]
    else:
        with pytest.raises(Rejected, match="file-not-authorized"):
            agent.research("Q3.pdf")
        assert not tool.has_read
        assert proofs == requests == []


@pytest.mark.unit
@pytest.mark.parametrize(
    ("group", "component"),
    [
        ("swarmauri.agents", WimseResearchAgent),
        ("swarmauri.tools", WimseFileTool),
    ],
)
def test_component_entry_point(group, component):
    (entry,) = entry_points(group=group, name=component.__name__)
    assert entry.load() is component
