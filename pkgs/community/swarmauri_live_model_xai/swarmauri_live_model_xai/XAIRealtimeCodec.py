import base64
import json
from swarmauri_base.live_models.events.AudioDeltaEvent import AudioDeltaEvent
from swarmauri_base.live_models.events.SessionErrorEvent import (
    SessionErrorEvent,
)
from swarmauri_base.live_models.events.TextDeltaEvent import TextDeltaEvent
from swarmauri_base.live_models.events.ToolCallEvent import ToolCallEvent
from swarmauri_base.live_models.events.TurnCompleteEvent import (
    TurnCompleteEvent,
)


class XAIRealtimeCodec:
    def encode(self, input_data):
        if input_data.kind == "text":
            return json.dumps(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": input_data.payload}
                        ],
                    },
                }
            )
        if input_data.kind == "audio":
            return json.dumps(
                {
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(input_data.payload).decode(),
                }
            )
        if input_data.kind == "tool_result":
            return json.dumps(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": input_data.call_id,
                        "output": json.dumps(input_data.payload),
                    },
                }
            )
        if input_data.kind == "interrupt":
            return json.dumps({"type": "response.cancel"})
        return json.dumps({"type": "response.create"})

    def decode(self, message):
        data = json.loads(message)
        kind = data.get("type", "")
        correlation = {
            "provider_event_id": data.get("event_id"),
            "call_id": data.get("call_id"),
        }
        if kind.endswith("text.delta"):
            return [
                TextDeltaEvent(
                    payload=data.get("delta", ""), correlation=correlation
                )
            ]
        if kind.endswith("audio.delta"):
            return [
                AudioDeltaEvent(
                    payload=base64.b64decode(data.get("delta", "")),
                    correlation=correlation,
                )
            ]
        if kind == "response.function_call_arguments.done":
            args = data.get("arguments", {})
            return [
                ToolCallEvent(
                    call_id=data.get("call_id", ""),
                    tool_name=data.get("name", ""),
                    arguments=json.loads(args)
                    if isinstance(args, str)
                    else args,
                    correlation=correlation,
                )
            ]
        if kind == "response.done":
            return [TurnCompleteEvent(correlation=correlation)]
        if kind == "error":
            return [
                SessionErrorEvent(
                    message=str(data.get("error", data)),
                    correlation=correlation,
                )
            ]
        return []
