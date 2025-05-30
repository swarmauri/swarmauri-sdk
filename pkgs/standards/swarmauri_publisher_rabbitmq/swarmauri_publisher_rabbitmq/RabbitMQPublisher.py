from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import pika
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.publishers.PublishBase import PublishBase


@ComponentBase.register_model()
class RabbitMQPublisher(PublishBase):
    """
    Send JSON messages to RabbitMQ exchanges.
    Inherits from PublishBase.

    The publisher may be configured either via an AMQP URI or by
    supplying the individual ``host``/``port``/``username``/``password``
    parameters. If both styles are provided at once a ``ValueError``
    is raised. The ``exchange`` name must also be provided.
    """

    uri: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    exchange: str

    _connection: pika.BlockingConnection = PrivateAttr()
    _channel: pika.adapters.blocking_connection.BlockingChannel = PrivateAttr()

    def __init__(self, **data: Any):
        super().__init__(**data)

        individual_opts_present = any(
            v is not None for v in (self.host, self.port, self.username, self.password)
        )

        if self.uri and individual_opts_present:
            print(
                f"RabbitMQPublisher: uri={self.uri}, host={self.host}, port={self.port}, username={self.username}, password={self.password}"
            )
            raise ValueError(
                "Cannot specify both `uri` and individual host/port/username/password."
            )

        actual_amqp_uri: str

        if self.uri:
            actual_amqp_uri = self.uri
        else:
            if self.host is None:
                raise ValueError("When no `uri` is given, `host` is required.")
            auth = ""
            if self.username and self.password:
                auth = f"{quote_plus(self.username)}:{quote_plus(self.password)}@"
            elif self.username:
                auth = f"{quote_plus(self.username)}@"
            actual_amqp_uri = f"amqp://{auth}{self.host}:{self.port}/"

        params = pika.URLParameters(actual_amqp_uri)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
            exchange=self.exchange, exchange_type="direct", durable=True
        )

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """
        Publish ``payload`` to the configured ``exchange`` with ``channel`` as routing_key.
        """
        body = json.dumps(payload).encode()
        try:
            self._channel.basic_publish(
                exchange=self.exchange,
                routing_key=channel,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # Make messages persistent
                ),
            )
        except (
            pika.exceptions.AMQPConnectionError,
            pika.exceptions.ChannelClosedByBroker,
        ):
            # Basic reconnection logic or error handling
            self._connection.close()
            params = pika.URLParameters(self._connection.params.uri)
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.exchange_declare(
                exchange=self.exchange, exchange_type="direct", durable=True
            )
            self._channel.basic_publish(
                exchange=self.exchange,
                routing_key=channel,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )

    def __del__(self) -> None:
        try:
            if self._connection and not self._connection.is_closed:
                self._connection.close()
        except Exception:
            pass
