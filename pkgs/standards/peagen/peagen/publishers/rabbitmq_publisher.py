# File: rabbitmq_publisher.py
"""RabbitMQ message publisher implementation."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import pika


class RabbitMQPublisher:
    """Send JSON messages to RabbitMQ exchanges.

    The publisher may be configured either via an AMQP URI or by
    supplying the individual ``host``/``port``/``username``/``password``
    parameters. If both styles are provided at once a ``ValueError``
    is raised.
    """

    def __init__(
        self,
        *,
        uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        exchange: str = "",
        routing_key: str = "",
    ) -> None:
        if uri and any(v is not None for v in (host, port, username, password)):
            raise ValueError(
                "Cannot specify both `uri` and individual host/port/username/password."
            )

        if uri:
            amqp_uri = uri
        else:
            if host is None or port is None:
                raise ValueError(
                    "When no `uri` is given, `host` and `port` are required."
                )
            auth = ""
            if username and password:
                auth = f"{quote_plus(username)}:{quote_plus(password)}@"
            elif username:
                auth = f"{quote_plus(username)}@"
            amqp_uri = f"amqp://{auth}{host}:{port}/"

        params = pika.URLParameters(amqp_uri)
        self._exchange = exchange
        self._routing_key = routing_key
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def publish(self, routing_key: str, payload: Dict[str, Any]) -> None:
        """Publish ``payload`` to ``routing_key`` or the default route."""

        body = json.dumps(payload).encode()
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=routing_key or self._routing_key,
            body=body,
        )

    def __del__(self) -> None:
        try:
            self._connection.close()
        except Exception:
            pass
