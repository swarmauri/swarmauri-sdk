from swarmauri_base.live_models.inputs.ToolResultInput import ToolResultInput


class OpenAIRealtimeToolAdapter:
    def result(
        self, call_id: str, value: object, *, is_error: bool = False
    ) -> ToolResultInput:
        return ToolResultInput(
            call_id=call_id, payload=value, is_error=is_error
        )
