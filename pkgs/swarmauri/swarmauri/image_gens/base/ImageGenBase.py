from abc import abstractmethod
from typing import Optional, List, Literal
from pydantic import ConfigDict, model_validator, Field
from swarmauri_core.image_gens.IGenImage import IGenImage
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes


class ImageGenBase(IGenImage, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.IMAGE_GEN.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ImageGenBase"] = "ImageGenBase"

    @model_validator(mode="after")
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        name = values.name
        allowed_models = values.allowed_models
        if name and name not in allowed_models:
            raise ValueError(
                f"Model name {name} is not allowed. Choose from {allowed_models}"
            )
        return values

    @abstractmethod
    def generate_image(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        raise NotImplementedError("generate_image() not implemented in subclass yet.")

    @abstractmethod
    async def agenerate_image(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        raise NotImplementedError("agenerate_image() not implemented in subclass yet.")

    @abstractmethod
    def batch_generate(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        raise NotImplementedError("batch_generate() not implemented in subclass yet.")

    @abstractmethod
    async def abatch_generate(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        raise NotImplementedError("abatch_generate() not implemented in subclass yet.")
