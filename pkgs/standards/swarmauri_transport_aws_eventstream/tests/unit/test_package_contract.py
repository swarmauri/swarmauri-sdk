from importlib.metadata import entry_points, version

from swarmauri_transport_aws_eventstream import AwsEventStreamClient


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_transport_aws_eventstream")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.transports")
        if ep.name == "AwsEventStreamClient"
    )
    assert point.load() is AwsEventStreamClient
