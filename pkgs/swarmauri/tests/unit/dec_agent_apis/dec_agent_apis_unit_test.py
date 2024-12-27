import pytest
from swarmauri.dec_agent_apis.concrete.DecAgentAPI import DecAgentAPI
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def dec_agent_api():
    dec_agent_api = DecAgentAPI()
    return dec_agent_api


@pytest.mark.unit
def test_ubc_resource(dec_agent_api):
    assert dec_agent_api.resource == "DecAgentAPI"


@pytest.mark.unit
def test_ubc_type(dec_agent_api):
    assert dec_agent_api.type == "DecAgentAPI"


@pytest.mark.unit
def test_serialization(dec_agent_api):
    assert (
        dec_agent_api.id == DecAgentAPI.model_validate_json(dec_agent_api.model_dump_json()).id
    )
