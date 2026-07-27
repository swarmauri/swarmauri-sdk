from swarmauri_base.live_models import LiveConfigBase


class XAIRealtimeConfigMapper:
    def map(self, config: LiveConfigBase) -> dict:
        return {
            "type": "session.update",
            "session": {
                "modalities": config.requested_modalities,
                **config.provider_options.get("session", {}),
            },
        }
