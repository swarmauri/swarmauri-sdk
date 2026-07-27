import base64
import json
from typing import Any, Dict, List

from swarmauri_base.live_models import LiveEventBase, LiveInputBase
from swarmauri_base.live_models.events import (
    AudioDeltaEvent,
    InputTranscriptDeltaEvent,
    OutputTranscriptDeltaEvent,
    SessionErrorEvent,
    SessionLifecycleEvent,
    SessionResumptionEvent,
    TextDeltaEvent,
    ToolCallEvent,
    TurnCompleteEvent,
    UsageEvent,
)


class GeminiLiveCodec:
    def encode(self, input_data: LiveInputBase) -> str:
        if input_data.kind == "text":
            payload = {"realtimeInput": {"text": input_data.payload}}
        elif input_data.kind in {"audio", "image", "video"}:
            payload = {
                "realtimeInput": {
                    "mediaChunks": [
                        {
                            "mimeType": input_data.mime_type,
                            "data": base64.b64encode(
                                input_data.payload
                            ).decode(),
                        }
                    ]
                }
            }
        elif input_data.kind == "tool_result":
            payload = {
                "toolResponse": {
                    "functionResponses": [
                        {
                            "id": input_data.call_id,
                            "name": input_data.correlation_id or "tool",
                            "response": {"output": input_data.payload},
                        }
                    ]
                }
            }
        elif input_data.kind == "commit_turn":
            payload = {"realtimeInput": {"activityEnd": {}}}
        elif input_data.kind == "interrupt":
            payload = {"realtimeInput": {"activityStart": {}}}
        else:
            raise ValueError(
                f"Unsupported Gemini live input: {input_data.kind}"
            )
        return json.dumps(payload)

    def decode(self, message: str | bytes) -> List[LiveEventBase]:
        data: Dict[str, Any] = json.loads(message)
        events: List[LiveEventBase] = []
        server = data.get("serverContent", {})
        model_turn = server.get("modelTurn", {})
        correlation = {"provider_event_id": data.get("id")}

        for part in model_turn.get("parts", []):
            if "text" in part:
                events.append(
                    TextDeltaEvent(
                        payload=part["text"], correlation=correlation
                    )
                )
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and str(inline.get("mimeType", "")).startswith("audio/"):
                events.append(
                    AudioDeltaEvent(
                        payload=base64.b64decode(inline["data"]),
                        mime_type=inline.get("mimeType", "audio/pcm"),
                        correlation=correlation,
                    )
                )

        input_tx = server.get("inputTranscription", {})
        if input_tx.get("text"):
            events.append(
                InputTranscriptDeltaEvent(
                    payload=input_tx["text"], correlation=correlation
                )
            )
        output_tx = server.get("outputTranscription", {})
        if output_tx.get("text"):
            events.append(
                OutputTranscriptDeltaEvent(
                    payload=output_tx["text"], correlation=correlation
                )
            )
        if server.get("turnComplete"):
            events.append(TurnCompleteEvent(correlation=correlation))

        for call in data.get("toolCall", {}).get("functionCalls", []):
            events.append(
                ToolCallEvent(
                    call_id=call.get("id", call.get("name", "")),
                    tool_name=call["name"],
                    arguments=call.get("args", {}),
                    correlation=correlation,
                )
            )
        if data.get("usageMetadata"):
            usage = {
                key: int(value)
                for key, value in data["usageMetadata"].items()
                if isinstance(value, int)
            }
            events.append(UsageEvent(payload=usage, correlation=correlation))
        if data.get("sessionResumptionUpdate"):
            update = data["sessionResumptionUpdate"]
            events.append(
                SessionResumptionEvent(
                    token=update.get("newHandle"),
                    resumable=bool(update.get("resumable", True)),
                    correlation=correlation,
                )
            )
        if data.get("goAway"):
            events.append(
                SessionLifecycleEvent(
                    state="closing",
                    payload=data["goAway"],
                    correlation=correlation,
                )
            )
        if data.get("error"):
            events.append(
                SessionErrorEvent(
                    message=str(data["error"]), correlation=correlation
                )
            )
        return events
