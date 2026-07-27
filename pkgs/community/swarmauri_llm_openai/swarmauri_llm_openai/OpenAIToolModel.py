from typing import Optional
from pydantic import model_validator
from swarmauri_provider_openai import OpenAIProvider
from swarmauri_standard.llms.OpenAIToolModel import (
    OpenAIToolModel as _OpenAIToolModel,
)


class OpenAIToolModel(_OpenAIToolModel):
    provider: Optional[OpenAIProvider] = None

    @model_validator(mode="before")
    @classmethod
    def apply_provider(cls, data):
        if isinstance(data, dict) and isinstance(
            data.get("provider"), OpenAIProvider
        ):
            provider = data["provider"]
            data.setdefault("api_key", provider.api_key)
        return data


__all__ = ["OpenAIToolModel"]
