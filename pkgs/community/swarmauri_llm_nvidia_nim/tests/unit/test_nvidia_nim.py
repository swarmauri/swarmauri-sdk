import httpx
import pytest
from importlib.metadata import entry_points

from swarmauri_llm_nvidia_nim import NvidiaNIMModel, NvidiaNIMToolModel


@pytest.mark.unit
def test_models_use_nim_endpoints_without_network_on_init():
    model = NvidiaNIMModel(base_url="https://nim.example/v1", name="served")
    tool_model = NvidiaNIMToolModel(
        base_url="https://nim.example", name="served"
    )

    assert model._build_endpoint() == "https://nim.example/v1/chat/completions"
    assert (
        tool_model._build_endpoint()
        == "https://nim.example/v1/chat/completions"
    )
    assert model.allowed_models == ["served"]
    assert "tools" in tool_model.capabilities


@pytest.mark.unit
def test_model_discovery(monkeypatch):
    original_client = httpx.Client

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/models"
        return httpx.Response(200, json={"data": [{"id": "served-model"}]})

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    model = NvidiaNIMModel(
        base_url="https://nim.example", name="served", discover_models=True
    )
    assert model.allowed_models == ["served-model"]


@pytest.mark.unit
def test_api_key_is_not_serialized():
    model = NvidiaNIMModel(name="served", api_key="secret")
    assert "secret" not in model.model_dump_json()


@pytest.mark.unit
def test_entry_points_are_registered():
    llms = {entry.name for entry in entry_points(group="swarmauri.llms")}
    tool_llms = {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
    assert "NvidiaNIMModel" in llms
    assert "NvidiaNIMToolModel" in tool_llms
