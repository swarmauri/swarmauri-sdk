import httpx
import pytest
from importlib.metadata import entry_points

from swarmauri_llm_cloudflare import (
    CloudflareWorkersAIModel,
    CloudflareWorkersAIToolModel,
)


@pytest.mark.unit
def test_models_build_account_scoped_endpoints_without_network_on_init():
    model = CloudflareWorkersAIModel(
        account_id="acct", api_key="token", name="@cf/model"
    )
    tool_model = CloudflareWorkersAIToolModel(
        account_id="acct", api_key="token", name="@cf/tool-model"
    )

    expected = (
        "https://api.cloudflare.com/client/v4/accounts/acct/ai/v1/"
        "chat/completions"
    )
    assert model._build_endpoint() == expected
    assert tool_model._build_endpoint() == expected
    assert model.allowed_models == ["@cf/model"]
    assert "tools" in tool_model.capabilities


@pytest.mark.unit
def test_model_discovery(monkeypatch):
    original_client = httpx.Client

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/ai/models/search")
        assert request.headers["authorization"] == "Bearer token"
        return httpx.Response(200, json={"result": [{"name": "@cf/model"}]})

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    model = CloudflareWorkersAIModel(
        account_id="acct",
        api_key="token",
        name="@cf/default",
        discover_models=True,
    )
    assert model.allowed_models == ["@cf/model"]


@pytest.mark.unit
def test_credentials_are_not_serialized():
    model = CloudflareWorkersAIModel(
        account_id="acct", api_key="secret", name="@cf/model"
    )
    assert "secret" not in model.model_dump_json()


@pytest.mark.unit
def test_entry_points_are_registered():
    llms = {entry.name for entry in entry_points(group="swarmauri.llms")}
    tool_llms = {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
    assert "CloudflareWorkersAIModel" in llms
    assert "CloudflareWorkersAIToolModel" in tool_llms
