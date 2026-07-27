from swarmauri_base.live_models.inputs import ToolResultInput


class GeminiLiveToolAdapter:
    def result(
        self, call_id: str, name: str, value: object
    ) -> ToolResultInput:
        return ToolResultInput(
            call_id=call_id,
            correlation_id=name,
            payload=value,
        )
