from typing import Literal
from swarmauri.service_registries.base.ServiceRegistryBase import ServiceRegistryBase


class ServiceRegistry(ServiceRegistryBase):
    """
    Concrete implementation of the ServiceRegistryBase.
    """

    type: Literal["ServiceRegistry"] = "ServiceRegistry"
