from typing import Any

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_provider_gemini import GeminiToolSchemaConverter


class GeminiLiveConfigMapper:
    def __init__(self) -> None:
        self._tools = GeminiToolSchemaConverter()

    def map(self, model: str, config: LiveConfigBase) -> dict[str, Any]:
        generation = {
            "responseModalities": [
                modality.upper() for modality in config.requested_modalities
            ]
        }
        setup: dict[str, Any] = {
            "model": f"models/{model}",
            "generationConfig": generation,
        }
        if config.tools:
            setup["tools"] = [
                {
                    "functionDeclarations": [
                        self._tools.convert(tool) for tool in config.tools
                    ]
                }
            ]
        setup.update(config.provider_options.get("setup", {}))
        return {"setup": setup}
