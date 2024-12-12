from abc import ABC, abstractmethod


class IGenImage(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining image generating models.
    """

    @abstractmethod
    def generate_image(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def agenerate_image(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        pass

    @abstractmethod
    def batch_generate(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def abatch_generate(self, *args, **kwargs) -> any:
        """
        Generate images based on the input data provided to the model.
        """
        pass
