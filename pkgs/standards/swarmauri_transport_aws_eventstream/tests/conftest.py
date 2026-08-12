from swarmauri_base.transports.bidirectional.BidirectionalStreamClientBase import (  # noqa: E501
    BidirectionalStreamClientBase,
)
from swarmauri_tests_component import ComponentSpec
from swarmauri_transport_aws_eventstream import AwsEventStreamClient


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            AwsEventStreamClient,
            {},
            "Transport",
            None,
            BidirectionalStreamClientBase,
            excluded_fields=("sdk_client_factory",),
        )
    ]
