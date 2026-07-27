import base64
import json
from typing import Any, Dict, List

from swarmauri_base.live_models.LiveEventBase import LiveEventBase
from swarmauri_base.live_models.LiveInputBase import LiveInputBase
from swarmauri_base.live_models.events.AudioDeltaEvent import AudioDeltaEvent
from swarmauri_base.live_models.events.InputTranscriptDeltaEvent import (
    InputTranscriptDeltaEvent,
)
from swarmauri_base.live_models.events.InterruptionEvent import (
    InterruptionEvent,
)
from swarmauri_base.live_models.events.OutputTranscriptDeltaEvent import (
    OutputTranscriptDeltaEvent,
)
from swarmauri_base.live_models.events.SessionErrorEvent import (
    SessionErrorEvent,
)
from swarmauri_base.live_models.events.TextDeltaEvent import TextDeltaEvent
from swarmauri_base.live_models.events.ToolCallEvent import ToolCallEvent
from swarmauri_base.live_models.events.TurnCompleteEvent import (
    TurnCompleteEvent,
)
from swarmauri_base.live_models.events.UsageEvent import UsageEvent


class OpenAIRealtimeCodec:
    def encode(self, input_data: LiveInputBase) -> List[str]:
        if input_data.kind == "text":
            return [
                json.dumps(
                    {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": input_data.payload,
                                }
                            ],
                        },
                    }
                ),
                json.dumps({"type": "response.create"}),
            ]
        if input_data.kind == "audio":
            return [
                json.dumps(
                    {
                        "type": "input_audio_buffer.append",
                        "audio": base64.b64encode(input_data.payload).decode(),
                    }
                )
            ]
        if input_data.kind == "image":
            encoded = base64.b64encode(input_data.payload).decode()
            image_url = f"data:{input_data.mime_type};base64,{encoded}"
            return [
                json.dumps(
                    {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_image",
                                    "image_url": image_url,
                                }
                            ],
                        },
                    }
                )
            ]
        if input_data.kind == "tool_result":
            return [
                json.dumps(
                    {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": input_data.call_id,
                            "output": json.dumps(input_data.payload),
                        },
                    }
                ),
                json.dumps({"type": "response.create"}),
            ]
        if input_data.kind == "commit_turn":
            return [
                json.dumps({"type": "input_audio_buffer.commit"}),
                json.dumps({"type": "response.create"}),
            ]
        if input_data.kind == "interrupt":
            return [json.dumps({"type": "response.cancel"})]
        raise ValueError(
            f"Unsupported OpenAI realtime input: {input_data.kind}"
        )

    def decode(self, message: str | bytes) -> List[LiveEventBase]:
        data: Dict[str, Any] = json.loads(message)
        kind = data.get("type", "")
        correlation = {
            "provider_event_id": data.get("event_id"),
            "response_id": data.get("response_id")
            or data.get("response", {}).get("id"),
            "item_id": data.get("item_id"),
            "call_id": data.get("call_id"),
        }
        if kind in {"response.output_text.delta", "response.text.delta"}:
            return [
                TextDeltaEvent(
                    payload=data.get("delta", ""), correlation=correlation
                )
            ]
        if kind in {"response.output_audio.delta", "response.audio.delta"}:
            return [
                AudioDeltaEvent(
                    payload=base64.b64decode(data.get("delta", "")),
                    correlation=correlation,
                )
            ]
        if kind in {
            "response.output_audio_transcript.delta",
            "response.audio_transcript.delta",
        }:
            return [
                OutputTranscriptDeltaEvent(
                    payload=data.get("delta", ""), correlation=correlation
                )
            ]
        if "input_audio_transcription" in kind:
            text = data.get("delta") or data.get("transcript", "")
            return [
                InputTranscriptDeltaEvent(
                    payload=text, correlation=correlation
                )
            ]
        if kind == "response.function_call_arguments.done":
            arguments = data.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments or "{}")
            return [
                ToolCallEvent(
                    call_id=data.get("call_id", ""),
                    tool_name=data.get("name", ""),
                    arguments=arguments,
                    correlation=correlation,
                )
            ]
        if kind == "input_audio_buffer.speech_started":
            return [
                InterruptionEvent(
                    reason="speech_started", correlation=correlation
                )
            ]
        if kind == "response.done":
            events: List[LiveEventBase] = [
                TurnCompleteEvent(correlation=correlation)
            ]
            usage = data.get("response", {}).get("usage")
            if usage:
                events.append(
                    UsageEvent(
                        payload={
                            key: int(value)
                            for key, value in usage.items()
                            if isinstance(value, int)
                        },
                        correlation=correlation,
                    )
                )
            return events
        if kind == "error":
            return [
                SessionErrorEvent(
                    message=str(data.get("error", data)),
                    correlation=correlation,
                )
            ]
        return []
