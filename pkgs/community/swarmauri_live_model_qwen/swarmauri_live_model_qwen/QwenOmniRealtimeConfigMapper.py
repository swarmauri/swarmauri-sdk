from swarmauri_base.live_models import LiveConfigBase


class QwenOmniRealtimeConfigMapper:
    def map(self, config: LiveConfigBase) -> dict:
        return {
            "event_id": "swarmauri-setup",
            "type": "session.update",
            "session": {
                "modalities": config.requested_modalities,
                **config.provider_options.get("session", {}),
            },
        }
