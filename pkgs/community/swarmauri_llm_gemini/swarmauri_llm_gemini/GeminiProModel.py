from typing import Optional
from pydantic import model_validator
from swarmauri_provider_gemini import GeminiProvider
from swarmauri_standard.llms.GeminiProModel import (
    GeminiProModel as _GeminiProModel,
)


class GeminiProModel(_GeminiProModel):
    provider: Optional[GeminiProvider] = None

    @model_validator(mode="before")
    @classmethod
    def apply_provider(cls, data):
        if isinstance(data, dict) and isinstance(
            data.get("provider"), GeminiProvider
        ):
            provider = data["provider"]
            data.setdefault("api_key", provider.api_key)
        return data


__all__ = ["GeminiProModel"]
