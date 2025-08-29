"""Redis Pub/Sub publisher implementation."""

from __future__ import annotations

import json
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

import redis


class RedisPublisher:
    """Sync publisher for Redis Pub/Sub."""

    def __init__(
        self,
        *,
        uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        username: Optional[str] = None,
    ) -> None:
        individual_opts = any(
            v is not None for v in (host, port, db, password, username)
        )
        if uri and individual_opts:
            raise ValueError(
                "Cannot specify both `uri` and individual host/port/db/password/username."
            )

        if uri:
            redis_uri = uri
        else:
            if not (host and port is not None and db is not None):
                raise ValueError(
                    "When no `uri` is given, `host`, `port`, and `db` are required."
                )

            if username and password:
                auth = f"{quote_plus(username)}:{quote_plus(password)}@"
            elif password:
                auth = f":{quote_plus(password)}@"
            else:
                auth = ""

            redis_uri = f"redis://{auth}{host}:{port}/{db}"

        self._client: redis.Redis = redis.from_url(redis_uri, decode_responses=True)

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Send ``payload`` to ``channel`` as a JSON message."""
        self._client.publish(channel, json.dumps(payload))
