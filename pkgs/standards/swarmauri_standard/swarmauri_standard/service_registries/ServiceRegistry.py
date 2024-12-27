from typing import Literal
from swarmauri_base.service_registries.ServiceRegistryBase import ServiceRegistryBase


class ServiceRegistry(ServiceRegistryBase):
    """
    Concrete implementation of the ServiceRegistryBase.
    """

    type: Literal["ServiceRegistry"] = "ServiceRegistry"
