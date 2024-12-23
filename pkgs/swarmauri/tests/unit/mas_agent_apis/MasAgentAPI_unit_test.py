import pytest
from swarmauri.mas_agent_apis.concrete.MasAgentAPI import MasAgentAPI
from swarmauri.transports.concrete.PubSubTransport import PubSubTransport as Transport


@pytest.fixture
def mas_agent_api():
    """Set up the MasAgentAPIBase instance with a mocked transport."""
    transport = Transport()
    api = MasAgentAPI(transport=transport)
    return api


@pytest.mark.unit
def test_ubc_resource(mas_agent_api):
    assert mas_agent_api.resource == "MasAgentAPI"


@pytest.mark.unit
def test_ubc_type(mas_agent_api):
    assert mas_agent_api.type == "MasAgentAPI"


@pytest.mark.unit
def test_serialization(mas_agent_api):
    assert (
        mas_agent_api.id
        == MasAgentAPI.model_validate_json(mas_agent_api.model_dump_json()).id
    )


def test_send_message(mas_agent_api):
    """Test that send_message calls transport.send_message with correct arguments."""
    message = {"content": "Test Message"}
    recipient_id = "agent_123"

    mas_agent_api.send_message(message, recipient_id)

    mas_agent_api.transport.send_message.assert_called_once_with(message, recipient_id)


def test_subscribe(mas_agent_api):
    """Test that subscribe calls transport.subscribe with correct topic."""
    topic = "test_topic"

    mas_agent_api.subscribe(topic)


def test_publish(mas_agent_api):
    """Test that publish calls transport.publish with correct topic."""
    topic = "test_topic"

    mas_agent_api.publish(message=topic)
