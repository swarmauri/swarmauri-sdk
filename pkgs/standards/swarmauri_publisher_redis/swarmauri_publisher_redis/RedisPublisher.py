from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import redis
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.publishers.PublishBase import PublishBase


@ComponentBase.register_model()
class RedisPublisher(PublishBase):
    uri: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    db: Optional[int] = None
    password: Optional[str] = None
    username: Optional[str] = None

    _client: redis.Redis = PrivateAttr()

    def __init__(self, **data: Any):
        """
        Initializes the RedisPublisher.
        Pydantic V2 first populates the defined model fields (e.g., self.uri, self.host)
        from `data` and then calls this __init__ method.
        """
        super().__init__(**data)

        individual_opts_present = any(
            v is not None
            for v in (self.host, self.port, self.db, self.password, self.username)
        )

        # Validate configuration: cannot mix URI with individual components.
        if self.uri and individual_opts_present:
            raise ValueError(
                "Cannot specify both `uri` and individual host/port/db/password/username."
            )

        actual_redis_uri: str

        if self.uri:
            actual_redis_uri = self.uri
        elif self.host is not None and self.port is not None and self.db is not None:
            # Construct URI from individual components if URI is not provided.
            auth_segment = ""
            if self.username and self.password:
                auth_segment = (
                    f"{quote_plus(self.username)}:{quote_plus(self.password)}@"
                )
            elif self.password:
                auth_segment = f":{quote_plus(self.password)}@"

            actual_redis_uri = (
                f"redis://{auth_segment}{self.host}:{self.port}/{self.db}"
            )
        else:
            # If neither a full URI nor the complete set of host, port, and db are provided.
            raise ValueError(
                "Redis connection configuration is incomplete: provide `uri`, or all of (`host`, `port`, `db`)."
            )

        # Initialize the Redis client.
        self._client = redis.from_url(actual_redis_uri, decode_responses=True)

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Fire-and-forget JSON message to the given channel."""
        # The _client is initialized in __init__.
        self._client.publish(channel, json.dumps(payload))
