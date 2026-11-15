from typing import ClassVar
from uuid import uuid4

import httpx
from swarmauri_core.tool_llms import IToolStepModel, ProposedToolCall, ToolStep


class GeminiToolStepMixin(IToolStepModel):
    tool_step_protocol: ClassVar[str] = "gemini-generate-content"

    def initial_tool_history(self, prompt):
        return [{"role": "user", "parts": [{"text": prompt}]}]

    def propose_step(self, history, tools):
        payload = {
            "contents": list(history),
            "safetySettings": self._safety_settings,
        }
        if tools:
            payload["tools"] = [self._schema_convert_tools(tools)]
        base_url = getattr(self, "BASE_URL", None) or self._BASE_URL
        response = httpx.post(
            f"{base_url}/{self.name}:generateContent",
            params={"key": self.api_key.get_secret_value()},
            headers=self._headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        candidates = response.json().get("candidates") or []
        if not candidates or not candidates[0].get("content"):
            raise ValueError("Gemini returned no model content")
        item = candidates[0]["content"]
        parts = item.get("parts", [])
        calls = []
        for part in parts:
            if "functionCall" in part:
                call = part["functionCall"]
                calls.append(
                    ProposedToolCall(
                        call_id=call.get("id") or str(uuid4()),
                        name=call["name"],
                        arguments=call.get("args", {}),
                        provider_call_id=call.get("id"),
                    )
                )
        content = "".join(
            part.get("text", "") for part in parts if not part.get("thought")
        )
        return ToolStep([item], calls, content or None)

    def format_tool_results(self, results):
        parts = []
        for result in results:
            response = {
                "name": result.call.name,
                "response": {"result": result.value},
            }
            if result.call.provider_call_id is not None:
                response["id"] = result.call.provider_call_id
            parts.append({"functionResponse": response})
        return [{"role": "user", "parts": parts}]
