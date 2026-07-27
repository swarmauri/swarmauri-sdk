from typing import Any, Dict

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_provider_openai import OpenAIToolSchemaConverter


class OpenAIRealtimeConfigMapper:
    def map(self, config: LiveConfigBase) -> Dict[str, Any]:
        session: Dict[str, Any] = {
            "type": "realtime",
            "output_modalities": config.requested_modalities,
        }
        if config.tools:
            converter = OpenAIToolSchemaConverter()
            session["tools"] = [
                converter.convert(tool) for tool in config.tools
            ]
        session.update(config.provider_options.get("session", {}))
        return {"type": "session.update", "session": session}
