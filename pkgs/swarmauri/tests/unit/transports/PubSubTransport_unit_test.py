import pytest
import asyncio
from uuid import UUID
from typing import Any
from swarmauri.transports.concrete.PubSubTransport import (
    PubSubTransport,
)
from swarmauri.utils.timeout_wrapper import timeout
import logging


@pytest.fixture
def pubsub_transport():
    transport = PubSubTransport()
    return transport


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(pubsub_transport):
    assert pubsub_transport.resource == "Transport"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(pubsub_transport):
    assert pubsub_transport.type == "PubSubTransport"


@timeout(5)
@pytest.mark.unit
def test_serialization(pubsub_transport):
    assert (
        pubsub_transport.id
        == PubSubTransport.model_validate_json(pubsub_transport.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_subscribe(pubsub_transport):
    topic = "test_topic"
    subscriber_id = await pubsub_transport.subscribe(topic)

    # Validate subscriber ID format
    assert isinstance(UUID(subscriber_id), UUID)

    # Ensure subscriber is added to the topic
    assert subscriber_id in pubsub_transport._topics[topic]


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsubscribe(pubsub_transport):
    topic = "test_topic"
    subscriber_id = await pubsub_transport.subscribe(topic)

    await pubsub_transport.unsubscribe(topic, subscriber_id)

    # Ensure subscriber is removed from the topic
    assert subscriber_id not in pubsub_transport._topics.get(topic, set())


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_publish_and_receive(pubsub_transport):
    topic = "test_topic"
    subscriber_id = await pubsub_transport.subscribe(topic)

    message = "Hello, PubSub!"
    await pubsub_transport.publish(topic, message)

    # Ensure the subscriber receives the message
    received_message = await pubsub_transport.receive(subscriber_id)
    assert received_message == message


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_broadcast(pubsub_transport):
    topic1 = "topic1"
    topic2 = "topic2"
    subscriber_id1 = await pubsub_transport.subscribe(topic1)
    subscriber_id2 = await pubsub_transport.subscribe(topic2)

    message = "Broadcast Message"
    pubsub_transport.broadcast("sender_id", message)

    # Ensure both subscribers receive the message
    received_message1 = await pubsub_transport.receive(subscriber_id1)
    received_message2 = await pubsub_transport.receive(subscriber_id2)
    assert received_message1 == message
    assert received_message2 == message


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_multicast(pubsub_transport):
    topic1 = "topic1"
    topic2 = "topic2"
    topic3 = "topic3"
    subscriber_id1 = await pubsub_transport.subscribe(topic1)
    subscriber_id2 = await pubsub_transport.subscribe(topic2)
    subscriber_id3 = await pubsub_transport.subscribe(topic3)

    message = "Multicast Message"
    pubsub_transport.multicast("sender_id", [topic1, topic2], message)

    # Ensure only subscribers of specified topics receive the message
    received_message1 = await pubsub_transport.receive(subscriber_id1)
    received_message2 = await pubsub_transport.receive(subscriber_id2)
    assert received_message1 == message
    assert received_message2 == message

    try:
        await asyncio.wait_for(pubsub_transport.receive(subscriber_id3), timeout=1.0)
        pytest.fail("Expected no message, but received one.")
    except asyncio.TimeoutError:
        pass


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_receive_no_messages(pubsub_transport):
    topic = "test_topic"
    subscriber_id = await pubsub_transport.subscribe(topic)

    try:
        await asyncio.wait_for(pubsub_transport.receive(subscriber_id), timeout=1.0)
        pytest.fail("Expected no message, but received one.")
    except asyncio.TimeoutError:
        pass
