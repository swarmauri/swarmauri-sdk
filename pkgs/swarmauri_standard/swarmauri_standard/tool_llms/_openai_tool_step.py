import json
from typing import ClassVar

import httpx
from swarmauri_core.tool_llms import IToolStepModel, ProposedToolCall, ToolStep


class OpenAIToolStepMixin(IToolStepModel):
    tool_step_protocol: ClassVar[str] = "openai-chat-completions"

    def initial_tool_history(self, prompt):
        return [{"role": "user", "content": prompt}]

    def propose_tool_step(self, messages, tools):
        """Return an assistant message without executing its tool calls."""
        payload = {"model": self.name, "messages": list(messages)}
        if tools:
            payload["tools"] = self._schema_convert_tools(tools)
            payload["parallel_tool_calls"] = False
        response = httpx.post(
            getattr(self, "BASE_URL", None) or self._BASE_URL,
            headers=self._headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        return {
            key: message[key]
            for key in ("role", "content", "tool_calls")
            if key in message
        }

    def propose_step(self, history, tools):
        message = self.propose_tool_step(history, tools)
        calls = [
            ProposedToolCall(
                call_id=call["id"],
                name=call["function"]["name"],
                arguments=call["function"]["arguments"],
                provider_call_id=call["id"],
            )
            for call in message.get("tool_calls") or []
        ]
        return ToolStep([message], calls, message.get("content"))

    def format_tool_results(self, results):
        return [
            {
                "role": "tool",
                "tool_call_id": result.call.provider_call_id
                or result.call.call_id,
                "content": json.dumps(result.value),
            }
            for result in results
        ]
