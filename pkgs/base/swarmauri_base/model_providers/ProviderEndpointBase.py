"""Common provider endpoint settings."""

from typing import Literal, Optional

from swarmauri_base.ComponentBase import ComponentBase


class ProviderEndpointBase(ComponentBase):
    base_url: Optional[str] = None
    region: Optional[str] = None
    type: Literal["ProviderEndpointBase"] = "ProviderEndpointBase"
