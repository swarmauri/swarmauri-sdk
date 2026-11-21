from typing import Optional, Literal
import asyncio
from pydantic import ConfigDict, Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.vlms.IPredictVision import IPredictVision


class VCMBase(IPredictVision, ComponentBase):
    resource: Optional[str] = Field(default="VCM", frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["VCMBase"] = "VCMBase"

    def predict_vision(self, *args, **kwargs):
        raise NotImplementedError("Predict not implemented in subclass yet.")

    async def apredict_vision(self, *args, **kwargs):
        return await asyncio.to_thread(self.predict_vision, *args, **kwargs)

    def batch(self, images, **kwargs):
        return [self.predict_vision(image, **kwargs) for image in images]

    async def abatch(self, images, **kwargs):
        return await asyncio.gather(
            *(self.apredict_vision(image, **kwargs) for image in images)
        )
