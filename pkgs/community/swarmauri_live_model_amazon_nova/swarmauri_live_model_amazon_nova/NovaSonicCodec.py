import base64
from swarmauri_base.live_models.events import (
    AudioDeltaEvent,
    SessionErrorEvent,
    TextDeltaEvent,
    ToolCallEvent,
    TurnCompleteEvent,
    UsageEvent,
)


class NovaSonicCodec:
    def encode(self, input_data):
        if input_data.kind == "audio":
            return {
                "event": {
                    "audioInput": {
                        "content": base64.b64encode(
                            input_data.payload
                        ).decode()
                    }
                }
            }
        if input_data.kind == "text":
            return {"event": {"textInput": {"content": input_data.payload}}}
        if input_data.kind == "tool_result":
            return {
                "event": {
                    "toolResult": {
                        "toolUseId": input_data.call_id,
                        "content": [{"json": input_data.payload}],
                        "status": "error"
                        if input_data.is_error
                        else "success",
                    }
                }
            }
        if input_data.kind == "commit_turn":
            return {"event": {"contentEnd": {}}}
        if input_data.kind == "interrupt":
            return {"event": {"playbackCompletion": {}}}
        raise ValueError(f"Unsupported Nova Sonic input: {input_data.kind}")

    def decode(self, data):
        event = data.get("event", data)
        if "audioOutput" in event:
            return [
                AudioDeltaEvent(
                    payload=base64.b64decode(
                        event["audioOutput"].get("content", "")
                    )
                )
            ]
        if "textOutput" in event:
            return [
                TextDeltaEvent(payload=event["textOutput"].get("content", ""))
            ]
        if "toolUse" in event:
            use = event["toolUse"]
            return [
                ToolCallEvent(
                    call_id=use.get("toolUseId", ""),
                    tool_name=use.get("toolName", ""),
                    arguments=use.get("content", {}),
                )
            ]
        if "completionEnd" in event or "contentEnd" in event:
            return [TurnCompleteEvent()]
        if "usageEvent" in event:
            return [
                UsageEvent(
                    payload={
                        key: int(value)
                        for key, value in event["usageEvent"].items()
                        if isinstance(value, int)
                    }
                )
            ]
        if "error" in event:
            return [SessionErrorEvent(message=str(event["error"]))]
        return []
