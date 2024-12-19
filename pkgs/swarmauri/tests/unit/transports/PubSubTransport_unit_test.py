import pytest
import asyncio
from swarmauri.transports.concrete.PubSubTransport import PubSubTransport


@pytest.fixture
def transport():
    return PubSubTransport()


@pytest.mark.unit
def test_ubc_resource(transport):
    assert transport.resource == "Transport"


@pytest.mark.unit
def test_ubc_type(transport):
    assert transport.type == "PubSubTransport"


@pytest.mark.unit
def test_serialization(transport):
    assert (
        transport.id
        == PubSubTransport.model_validate_json(transport.model_dump_json()).id
    )


@pytest.mark.asyncio
async def test_send(transport):
    # Setup
    subscriber_id = await transport.subscribe("test_topic")
    sender = "test_sender"
    message = "test_message"

    # Execute
    transport.send(sender, subscriber_id, message)

    # Verify
    received = await transport.receive(subscriber_id)
    assert received == (sender, message)


@pytest.mark.asyncio
async def test_send_invalid_recipient(transport):
    # Setup
    sender = "test_sender"
    invalid_recipient = "invalid_id"
    message = "test_message"

    # Verify raises error
    with pytest.raises(ValueError):
        transport.send(sender, invalid_recipient, message)


@pytest.mark.asyncio
async def test_broadcast(transport):
    # Setup
    subscriber1_id = await transport.subscribe("topic1")
    subscriber2_id = await transport.subscribe("topic2")
    sender = "test_sender"
    message = "broadcast_message"

    # Execute
    transport.broadcast(sender, message)

    # Verify all subscribers received message
    received1 = await transport.receive(subscriber1_id)
    received2 = await transport.receive(subscriber2_id)
    assert received1 == (sender, message)
    assert received2 == (sender, message)


@pytest.mark.asyncio
async def test_multicast(transport):
    # Setup
    subscriber1_id = await transport.subscribe("topic1")
    subscriber2_id = await transport.subscribe("topic2")
    subscriber3_id = await transport.subscribe("topic3")
    recipients = [subscriber1_id, subscriber3_id]
    sender = "test_sender"
    message = "multicast_message"

    # Execute
    transport.multicast(sender, recipients, message)

    # Verify target recipients received message
    received1 = await transport.receive(subscriber1_id)
    received3 = await transport.receive(subscriber3_id)
    assert received1 == (sender, message)
    assert received3 == (sender, message)

    # Verify non-target didn't receive
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(transport.receive(subscriber2_id), timeout=0.1)


@pytest.mark.asyncio
async def test_multicast_with_invalid_recipient(transport):
    # Setup
    subscriber_id = await transport.subscribe("topic1")
    recipients = [subscriber_id, "invalid_id"]
    sender = "test_sender"
    message = "multicast_message"

    # Execute - should not raise error for invalid recipient
    transport.multicast(sender, recipients, message)

    # Verify valid recipient still receives
    received = await transport.receive(subscriber_id)
    assert received == (sender, message)
