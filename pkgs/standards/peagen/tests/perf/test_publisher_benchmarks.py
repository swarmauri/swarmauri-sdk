import os
import pytest

from peagen.plugins.publishers.redis_publisher import RedisPublisher
from peagen.plugins.publishers.webhook_publisher import WebhookPublisher
from peagen.plugins.publishers.rabbitmq_publisher import RabbitMQPublisher


@pytest.mark.perf
def test_webhook_publisher_benchmark(benchmark):
    pub = WebhookPublisher()
    if not hasattr(pub, "publish"):
        pytest.skip("publish not implemented")
    benchmark(pub.publish, "http://example.com", {"msg": "x"})


@pytest.mark.perf
def test_rabbitmq_publisher_benchmark(benchmark):
    pub = RabbitMQPublisher()
    if not hasattr(pub, "publish"):
        pytest.skip("publish not implemented")
    benchmark(pub.publish, "queue", {"msg": "x"})


@pytest.mark.perf
def test_redis_publisher_benchmark(benchmark):
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL not set")
    pub = RedisPublisher(uri=redis_url)
    benchmark(pub.publish, "chan", {"msg": "x"})
