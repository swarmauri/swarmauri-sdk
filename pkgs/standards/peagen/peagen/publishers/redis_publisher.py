# File: redis_publisher.py
"""Redis Pub/Sub publisher implementation."""

from __future__ import annotations
import json
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

import redis


class RedisPublisher:
    """
    Sync implementation of the IPublish contract for Redis Pub/Sub.
    Supports initialization via:
      • uri="<scheme>://[:password@]host:port/db"  OR
      • host, port, db, password, username kwargs

    If `uri` is provided alongside any of (host, port, db, password, username),
    an exception is raised to avoid ambiguity.
    """

    def __init__(
        self,
        *,
        uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        username: Optional[str] = None,
    ):
        # 1) reject mixed config
        individual_opts = any(
            v is not None for v in (host, port, db, password, username)
        )
        if uri and individual_opts:
            raise ValueError(
                "Cannot specify both `uri` and individual host/port/db/password/username."
            )

        # 2) determine the actual URI
        if uri:
            redis_uri = uri

        else:
            # all individual opts must at least include host & port & db
            if not (host and port is not None and db is not None):
                raise ValueError(
                    "When no `uri` is given, `host`, `port`, and `db` are required."
                )

            # build auth segment
            if username and password:
                auth = f"{quote_plus(username)}:{quote_plus(password)}@"
            elif password:
                auth = f":{quote_plus(password)}@"
            else:
                auth = ""

            # assume default scheme redis://
            redis_uri = f"redis://{auth}{host}:{port}/{db}"

        # 3) create the client
        self._client: redis.Redis = redis.from_url(redis_uri, decode_responses=True)

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Fire-and-forget JSON message to the given channel."""
        self._client.publish(channel, json.dumps(payload))
