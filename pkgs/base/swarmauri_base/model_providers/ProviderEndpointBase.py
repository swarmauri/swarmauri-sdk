"""Common provider endpoint settings."""

from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase


class ProviderEndpointBase(ComponentBase):
    base_url: str | None = None
    region: str | None = None
    type: Literal["ProviderEndpointBase"] = "ProviderEndpointBase"
