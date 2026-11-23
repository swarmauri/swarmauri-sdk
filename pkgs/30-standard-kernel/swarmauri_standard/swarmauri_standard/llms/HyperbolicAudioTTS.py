"""Keep the legacy LLM-named retired Hyperbolic audio import."""

import warnings
from typing import Literal
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_standard.tts.HyperbolicTTS import HyperbolicTTS, RETIRED_MESSAGE

warnings.warn(RETIRED_MESSAGE, FutureWarning, stacklevel=2)


@ComponentBase.register_type(LLMBase, "HyperbolicAudioTTS")
class HyperbolicAudioTTS(HyperbolicTTS, LLMBase):
    """Retain serialized identity while disabling the decommissioned API."""

    type: Literal["HyperbolicAudioTTS"] = "HyperbolicAudioTTS"
    resource: str | None = Field(default=ResourceTypes.LLM.value, frozen=True)
