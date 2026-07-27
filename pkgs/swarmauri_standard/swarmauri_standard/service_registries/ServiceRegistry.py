from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.service_registries.ServiceRegistryBase import (
    ServiceRegistryBase,
)


@ComponentBase.register_type(ServiceRegistryBase, "ServiceRegistry")
class ServiceRegistry(ServiceRegistryBase):
    """
    Concrete implementation of the ServiceRegistryBase.
    """

    type: Literal["ServiceRegistry"] = "ServiceRegistry"
