from swarmauri_base.live_models.inputs.ToolResultInput import ToolResultInput


class XAIRealtimeToolAdapter:
    def result(self, call_id, value):
        return ToolResultInput(call_id=call_id, payload=value)
