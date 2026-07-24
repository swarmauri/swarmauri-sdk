"""HTTP transport helpers for provider-native chat model classes."""

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional

import httpx

from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.utils.duration_manager import DurationManager
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


def format_messages(messages: List[Any]) -> List[Dict[str, Any]]:
    properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
    return [
        message.model_dump(include=properties, exclude_none=True)
        for message in messages
    ]


def chat_payload(
    model: Any,
    messages: List[Dict[str, Any]],
    *,
    temperature: float,
    max_tokens: int,
    top_p: float,
    enable_json: bool,
    stop: Optional[List[str]],
    stream: bool = False,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model": model.name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "stop": stop or [],
    }
    if enable_json:
        payload["response_format"] = {"type": "json_object"}
    if stream:
        payload["stream"] = True
        if model.include_usage:
            payload["stream_options"] = {"include_usage": True}
    return payload


def _usage(data: Dict[str, Any], prompt: float, completion: float = 0.0):
    return UsageData(
        prompt_tokens=data.get("prompt_tokens", 0),
        completion_tokens=data.get("completion_tokens", 0),
        total_tokens=data.get("total_tokens", 0),
        prompt_time=prompt,
        completion_time=completion,
        total_time=prompt + completion,
    )


def _add_agent(
    model: Any,
    conversation: Any,
    content: str,
    usage_data: Optional[Dict[str, Any]] = None,
    prompt_time: float = 0.0,
    completion_time: float = 0.0,
) -> None:
    usage = None
    if model.include_usage:
        usage = _usage(usage_data or {}, prompt_time, completion_time)
    conversation.add_message(AgentMessage(content=content, usage=usage))


@retry_on_status_codes()
def predict_chat(
    model: Any,
    conversation: Any,
    temperature: float = 0.7,
    max_tokens: int = 256,
    top_p: float = 1.0,
    enable_json: bool = False,
    stop: Optional[List[str]] = None,
):
    payload = chat_payload(
        model,
        format_messages(conversation.history),
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        enable_json=enable_json,
        stop=stop,
    )
    with DurationManager() as timer:
        with httpx.Client(timeout=model.timeout) as client:
            response = client.post(
                model._build_endpoint(),
                headers=model._build_headers(),
                json=payload,
            )
            response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"].get("content") or ""
    _add_agent(model, conversation, content, data.get("usage"), timer.duration)
    return conversation


@retry_on_status_codes()
async def apredict_chat(
    model: Any,
    conversation: Any,
    temperature: float = 0.7,
    max_tokens: int = 256,
    top_p: float = 1.0,
    enable_json: bool = False,
    stop: Optional[List[str]] = None,
):
    payload = chat_payload(
        model,
        format_messages(conversation.history),
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        enable_json=enable_json,
        stop=stop,
    )
    with DurationManager() as timer:
        async with httpx.AsyncClient(timeout=model.timeout) as client:
            response = await client.post(
                model._build_endpoint(),
                headers=model._build_headers(),
                json=payload,
            )
            response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"].get("content") or ""
    _add_agent(model, conversation, content, data.get("usage"), timer.duration)
    return conversation


def _parse_sse(line: str) -> tuple[Optional[str], Dict[str, Any]]:
    if not line.startswith("data: "):
        return None, {}
    raw = line[6:].strip()
    if not raw or raw == "[DONE]":
        return None, {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, {}
    choices = data.get("choices") or []
    content = (
        (choices[0].get("delta") or {}).get("content") if choices else None
    )
    return content, data.get("usage") or {}


def stream_chat(
    model: Any,
    conversation: Any,
    temperature: float = 0.7,
    max_tokens: int = 256,
    top_p: float = 1.0,
    enable_json: bool = False,
    stop: Optional[List[str]] = None,
) -> Generator[str, None, None]:
    payload = chat_payload(
        model,
        format_messages(conversation.history),
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        enable_json=enable_json,
        stop=stop,
        stream=True,
    )
    content = ""
    usage_data: Dict[str, Any] = {}
    with DurationManager() as prompt_timer:
        with httpx.Client(timeout=model.timeout) as client:
            with client.stream(
                "POST",
                model._build_endpoint(),
                headers=model._build_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                with DurationManager() as completion_timer:
                    for line in response.iter_lines():
                        delta, usage = _parse_sse(line)
                        usage_data = usage or usage_data
                        if delta is not None:
                            content += delta
                            yield delta
    _add_agent(
        model,
        conversation,
        content,
        usage_data,
        prompt_timer.duration,
        completion_timer.duration,
    )


async def astream_chat(
    model: Any,
    conversation: Any,
    temperature: float = 0.7,
    max_tokens: int = 256,
    top_p: float = 1.0,
    enable_json: bool = False,
    stop: Optional[List[str]] = None,
) -> AsyncGenerator[str, None]:
    payload = chat_payload(
        model,
        format_messages(conversation.history),
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        enable_json=enable_json,
        stop=stop,
        stream=True,
    )
    content = ""
    usage_data: Dict[str, Any] = {}
    with DurationManager() as prompt_timer:
        async with httpx.AsyncClient(timeout=model.timeout) as client:
            async with client.stream(
                "POST",
                model._build_endpoint(),
                headers=model._build_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                with DurationManager() as completion_timer:
                    async for line in response.aiter_lines():
                        delta, usage = _parse_sse(line)
                        usage_data = usage or usage_data
                        if delta is not None:
                            content += delta
                            yield delta
    _add_agent(
        model,
        conversation,
        content,
        usage_data,
        prompt_timer.duration,
        completion_timer.duration,
    )


def batch_chat(model: Any, conversations: List[Any], **kwargs) -> List[Any]:
    return [
        predict_chat(model, conversation, **kwargs)
        for conversation in conversations
    ]


async def abatch_chat(
    model: Any,
    conversations: List[Any],
    max_concurrent: int = 5,
    **kwargs,
) -> List[Any]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def run(conversation: Any):
        async with semaphore:
            return await apredict_chat(model, conversation, **kwargs)

    return await asyncio.gather(*(run(item) for item in conversations))


def tool_payload(
    model: Any,
    messages: List[Dict[str, Any]],
    toolkit: Any,
    tool_choice: Any,
    temperature: float,
    max_tokens: int,
    stream: bool = False,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model": model.name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if toolkit is not None:
        payload["tools"] = model._schema_convert_tools(toolkit.tools)
        payload["tool_choice"] = tool_choice or "auto"
    if stream:
        payload["stream"] = True
    return payload


def _execute_tools(
    model: Any, tool_calls: List[Dict[str, Any]], toolkit: Any
) -> List[Dict[str, Any]]:
    messages = []
    for call in tool_calls:
        name = call["function"]["name"]
        function = toolkit.get_tool_by_name(name)
        result = function(**json.loads(call["function"]["arguments"]))
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call["id"],
                "name": name,
                "content": json.dumps(result),
            }
        )
    return messages


def _record_tool_turn(
    conversation: Any,
    provider_message: Dict[str, Any],
    tool_messages: List[Dict[str, Any]],
) -> None:
    conversation.add_message(
        AgentMessage(
            content=provider_message.get("content"),
            tool_calls=provider_message.get("tool_calls"),
        )
    )
    conversation.add_messages(
        [
            FunctionMessage(
                tool_call_id=message["tool_call_id"],
                name=message["name"],
                content=message["content"],
            )
            for message in tool_messages
        ]
    )


def _post_tool(model: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
    with httpx.Client(timeout=model.timeout) as client:
        response = client.post(
            model._build_endpoint(),
            headers=model._build_headers(),
            json=payload,
        )
        response.raise_for_status()
    return response.json()["choices"][0]["message"]


async def _apost_tool(model: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=model.timeout) as client:
        response = await client.post(
            model._build_endpoint(),
            headers=model._build_headers(),
            json=payload,
        )
        response.raise_for_status()
    return response.json()["choices"][0]["message"]


@retry_on_status_codes()
def predict_tools(
    model: Any,
    conversation: Any,
    toolkit: Any,
    tool_choice: Any = None,
    multiturn: bool = True,
    temperature: float = 0.7,
    max_tokens: int = 1024,
):
    messages = format_messages(conversation.history)
    payload = tool_payload(
        model, messages, toolkit, tool_choice, temperature, max_tokens
    )
    provider_message = _post_tool(model, payload)
    calls = provider_message.get("tool_calls") or []
    if not calls:
        conversation.add_message(
            AgentMessage(content=provider_message.get("content") or "")
        )
        return conversation
    tool_messages = _execute_tools(model, calls, toolkit)
    _record_tool_turn(conversation, provider_message, tool_messages)
    if multiturn:
        follow_up = tool_payload(
            model,
            messages + [provider_message] + tool_messages,
            None,
            None,
            temperature,
            max_tokens,
        )
        final = _post_tool(model, follow_up)
        conversation.add_message(
            AgentMessage(content=final.get("content") or "")
        )
    return conversation


@retry_on_status_codes()
async def apredict_tools(
    model: Any,
    conversation: Any,
    toolkit: Any,
    tool_choice: Any = None,
    multiturn: bool = True,
    temperature: float = 0.7,
    max_tokens: int = 1024,
):
    messages = format_messages(conversation.history)
    payload = tool_payload(
        model, messages, toolkit, tool_choice, temperature, max_tokens
    )
    provider_message = await _apost_tool(model, payload)
    calls = provider_message.get("tool_calls") or []
    if not calls:
        conversation.add_message(
            AgentMessage(content=provider_message.get("content") or "")
        )
        return conversation
    tool_messages = _execute_tools(model, calls, toolkit)
    _record_tool_turn(conversation, provider_message, tool_messages)
    if multiturn:
        follow_up = tool_payload(
            model,
            messages + [provider_message] + tool_messages,
            None,
            None,
            temperature,
            max_tokens,
        )
        final = await _apost_tool(model, follow_up)
        conversation.add_message(
            AgentMessage(content=final.get("content") or "")
        )
    return conversation


def stream_tools(
    model: Any,
    conversation: Any,
    toolkit: Any,
    tool_choice: Any = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> Generator[str, None, None]:
    messages = format_messages(conversation.history)
    first = _post_tool(
        model,
        tool_payload(
            model, messages, toolkit, tool_choice, temperature, max_tokens
        ),
    )
    calls = first.get("tool_calls") or []
    if not calls:
        content = first.get("content") or ""
        conversation.add_message(AgentMessage(content=content))
        if content:
            yield content
        return
    tool_messages = _execute_tools(model, calls, toolkit)
    _record_tool_turn(conversation, first, tool_messages)
    payload = tool_payload(
        model,
        messages + [first] + tool_messages,
        None,
        None,
        temperature,
        max_tokens,
        stream=True,
    )
    content = ""
    with (
        httpx.Client(timeout=model.timeout) as client,
        client.stream(
            "POST",
            model._build_endpoint(),
            headers=model._build_headers(),
            json=payload,
        ) as response,
    ):
        response.raise_for_status()
        for line in response.iter_lines():
            delta, _ = _parse_sse(line)
            if delta is not None:
                content += delta
                yield delta
    conversation.add_message(AgentMessage(content=content))


async def astream_tools(
    model: Any,
    conversation: Any,
    toolkit: Any,
    tool_choice: Any = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> AsyncGenerator[str, None]:
    messages = format_messages(conversation.history)
    first = await _apost_tool(
        model,
        tool_payload(
            model, messages, toolkit, tool_choice, temperature, max_tokens
        ),
    )
    calls = first.get("tool_calls") or []
    if not calls:
        content = first.get("content") or ""
        conversation.add_message(AgentMessage(content=content))
        if content:
            yield content
        return
    tool_messages = _execute_tools(model, calls, toolkit)
    _record_tool_turn(conversation, first, tool_messages)
    payload = tool_payload(
        model,
        messages + [first] + tool_messages,
        None,
        None,
        temperature,
        max_tokens,
        stream=True,
    )
    content = ""
    async with httpx.AsyncClient(timeout=model.timeout) as client:
        async with client.stream(
            "POST",
            model._build_endpoint(),
            headers=model._build_headers(),
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                delta, _ = _parse_sse(line)
                if delta is not None:
                    content += delta
                    yield delta
    conversation.add_message(AgentMessage(content=content))


def batch_tools(model: Any, conversations: List[Any], **kwargs) -> List[Any]:
    return [
        predict_tools(model, conversation, **kwargs)
        for conversation in conversations
    ]


async def abatch_tools(
    model: Any,
    conversations: List[Any],
    max_concurrent: int = 5,
    **kwargs,
) -> List[Any]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def run(conversation: Any):
        async with semaphore:
            return await apredict_tools(model, conversation, **kwargs)

    return await asyncio.gather(*(run(item) for item in conversations))
