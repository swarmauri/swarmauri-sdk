from typing import Literal
from swarmauri_base.service_registries.ServiceRegistryBase import ServiceRegistryBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ServiceRegistryBase, "ServiceRegistry")
class ServiceRegistry(ServiceRegistryBase):
    """
    Concrete implementation of the ServiceRegistryBase.
    """

    type: Literal["ServiceRegistry"] = "ServiceRegistry"
