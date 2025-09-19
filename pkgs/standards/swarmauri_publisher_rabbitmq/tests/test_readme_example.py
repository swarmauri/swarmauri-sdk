"""Execute the README quickstart to guard against drift."""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.mark.example
def test_readme_quickstart_example(monkeypatch: pytest.MonkeyPatch) -> None:
    """The README quickstart should continue to represent the real API."""

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    quickstart = _load_readme_quickstart(readme_path)

    publisher_module = importlib.import_module(
        "swarmauri_publisher_rabbitmq.RabbitMQPublisher"
    )

    published_messages: list[Dict[str, Any]] = []
    created_uris: list[str] = []

    class DummyChannel:
        def __init__(self) -> None:
            self.exchange_declarations: list[Dict[str, Any]] = []

        def exchange_declare(self, **kwargs: Any) -> None:
            self.exchange_declarations.append(dict(kwargs))

        def basic_publish(self, **kwargs: Any) -> None:
            published_messages.append(dict(kwargs))

    class DummyConnection:
        def __init__(self, params: Any) -> None:
            self.params = params
            self._closed = False
            self._channel = DummyChannel()

        def channel(self) -> DummyChannel:
            return self._channel

        def close(self) -> None:
            self._closed = True

        @property
        def is_closed(self) -> bool:  # pragma: no cover - trivial accessor
            return self._closed

    class DummyURLParameters:
        def __init__(self, uri: str) -> None:
            self.uri = uri
            created_uris.append(uri)

    class DummyBasicProperties:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

    monkeypatch.setattr(publisher_module.pika, "URLParameters", DummyURLParameters)
    monkeypatch.setattr(publisher_module.pika, "BlockingConnection", DummyConnection)
    monkeypatch.setattr(publisher_module.pika, "BasicProperties", DummyBasicProperties)

    namespace: Dict[str, Any] = {"__builtins__": __builtins__}
    exec(quickstart, namespace)

    publisher = namespace["publisher"]
    assert publisher.exchange == "demo_exchange"
    assert publisher._connection.params.uri == "amqp://guest:guest@localhost:5672/"
    assert publisher._channel.exchange_declarations == [
        {"exchange": "demo_exchange", "exchange_type": "direct", "durable": True}
    ]

    assert created_uris == ["amqp://guest:guest@localhost:5672/"]
    assert len(published_messages) == 1
    message = published_messages[0]
    assert message["exchange"] == "demo_exchange"
    assert message["routing_key"] == "demo.routing.key"
    assert json.loads(message["body"].decode("utf-8")) == {"message": "Hello RabbitMQ!"}
    assert message["properties"].kwargs["delivery_mode"] == (
        publisher_module.pika.spec.PERSISTENT_DELIVERY_MODE
    )


def _load_readme_quickstart(readme_path: Path) -> str:
    """Extract the quickstart snippet from the README."""

    text = readme_path.read_text(encoding="utf-8")
    match = re.search(
        r"```python\n(?P<code>.*?# README Quickstart Example.*?)\n```",
        text,
        re.DOTALL,
    )
    assert match, "Could not locate the README quickstart code block."
    return match.group("code")
