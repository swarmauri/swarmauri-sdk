# File: redis_publisher.py

from __future__ import annotations
import json
from typing import Dict, Any

import redis


class RedisPublisher:
    """
    Sync implementation of the IPublish contract for Redis Pub/Sub,
    supports both legacy REQUIREPASS and ACL-style authentication.
    """

    def __init__(self, uri: str):
        """
        Initialize Redis client from URL.

        Args:
            uri (str): full Redis URI, in one of the forms:
                       - Legacy auth (no ACL): "redis://:<password>@host:port/db"
                       - ACL user auth      : "redis://<username>:<password>@host:port/db"
        """
        self._client: redis.Redis = redis.from_url(uri, decode_responses=True)

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Fire-and-forget JSON message to the given channel."""
        self._client.publish(channel, json.dumps(payload))
