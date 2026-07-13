import json

from swarmauri_standard.tool_llms.ToolLLM import ToolLLM


def _tool_llm(**overrides):
    values = {
        "api_key": "secret",
        "BASE_URL": "https://provider.test/v1/chat/completions",
        "name": "provider-model",
        "allowed_models": ["provider-model"],
    }
    values.update(overrides)
    return ToolLLM(**values)


def test_tool_provider_hooks_and_runtime_state_are_not_serialized():
    class ProviderToolLLM(ToolLLM):
        capabilities = frozenset({"tools"})

        def _build_endpoint(self):
            return "https://override.test/tools"

    llm = ProviderToolLLM(**_tool_llm().model_dump(exclude={"type"}))

    assert llm._build_endpoint() == "https://override.test/tools"
    assert "_headers" not in llm.model_dump()
    assert "capabilities" not in llm.model_dump()
    assert "api_key" not in llm.model_dump()
    assert "secret" not in llm.model_dump_json()


def test_tool_payload_can_omit_tools_for_follow_up_turn():
    llm = _tool_llm()

    payload = llm._build_payload(
        [{"role": "user", "content": "hello"}],
        toolkit=None,
        tool_choice=None,
        temperature=0.1,
        max_tokens=20,
        stream=True,
    )

    assert payload["stream"] is True
    assert "tools" not in payload
    assert "tool_choice" not in payload


def test_tool_stream_parser_handles_content_usage_and_done_events():
    llm = _tool_llm()

    assert (
        llm._parse_stream_chunk(
            "data: "
            + json.dumps({"choices": [{"delta": {"content": "token"}}]})
        )
        == "token"
    )
    assert llm._parse_stream_chunk("data: [DONE]") is None
    assert llm._parse_stream_chunk("event: message") is None


def test_tool_model_name_can_be_discovered_after_validation():
    llm = ToolLLM(
        api_key="secret",
        BASE_URL="https://provider.test/v1/chat/completions",
        name="runtime-model",
    )

    assert llm.name == "runtime-model"
    assert llm.allowed_models == []
