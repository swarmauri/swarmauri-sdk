def test_package_imports_without_opening_sdk_connection():
    from swarmauri_transport_aws_eventstream import AwsEventStreamClient

    assert AwsEventStreamClient().type == "AwsEventStreamClient"
