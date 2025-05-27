from .RabbitMQPublisher import RabbitMQPublisher

__all__ = ["RabbitMQPublisher"]

try:
    # For Python 3.8 and newer
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_publisher_rabbitmq")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
