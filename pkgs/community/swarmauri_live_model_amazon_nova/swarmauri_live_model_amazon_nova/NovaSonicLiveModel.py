from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.live_models.LiveCapabilitiesBase import (
    LiveCapabilitiesBase,
)
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_core.transports.i_bidirectional_stream import (
    IBidirectionalStreamClient,
)
from swarmauri_provider_amazon_nova import AmazonNovaProvider
from swarmauri_transport_aws_eventstream import AwsEventStreamClient

from .NovaSonicConfigMapper import NovaSonicConfigMapper
from .NovaSonicLiveSession import NovaSonicLiveSession


@ComponentBase.register_type(LiveModelBase, "NovaSonicLiveModel")
class NovaSonicLiveModel(LiveModelBase):
    name: str = "amazon.nova-sonic-v1:0"
    provider: AmazonNovaProvider = Field(default_factory=AmazonNovaProvider)
    transport: IBidirectionalStreamClient = Field(
        default_factory=AwsEventStreamClient, exclude=True
    )
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=lambda: LiveCapabilitiesBase(
            input_modalities=frozenset({"text", "audio"}),
            output_modalities=frozenset({"text", "audio"}),
            features=frozenset({"tools"}),
            session_features=frozenset({"realtime", "bidirectional_http2"}),
        )
    )
    type: Literal["NovaSonicLiveModel"] = "NovaSonicLiveModel"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def aconnect(self, config: LiveConfigBase):
        connection_config = self.provider.prepare_connection(
            "live.connect", model=self.name
        )
        connection = await self.transport.aconnect(
            connection_config.resolved_url(),
            headers=connection_config.headers,
            **connection_config.transport_options,
        )
        return await NovaSonicLiveSession.create(
            connection, NovaSonicConfigMapper().map(self.name, config)
        )
