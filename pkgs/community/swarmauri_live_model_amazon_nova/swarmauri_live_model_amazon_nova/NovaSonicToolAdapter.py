from swarmauri_base.live_models.inputs import ToolResultInput


class NovaSonicToolAdapter:
    def result(self, call_id, value, *, is_error=False):
        return ToolResultInput(
            call_id=call_id, payload=value, is_error=is_error
        )
