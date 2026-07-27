from abc import ABC

from pydantic import ConfigDict, Field
from swarmauri_core.transports.i_bidirectional_stream import (
    IBidirectionalStreamClient,
)

from swarmauri_base.ComponentBase import ComponentBase


class BidirectionalStreamClientBase(
    IBidirectionalStreamClient, ComponentBase, ABC
):
    timeout: float = Field(default=60.0, gt=0)
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
