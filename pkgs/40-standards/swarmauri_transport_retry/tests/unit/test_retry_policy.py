from importlib.metadata import distribution

from swarmauri_transport_retry import (
    ExponentialBackoffRetryPolicy,
    RetryingHttpClient,
)


class Response:
    status_code = 429
    headers = {"Retry-After": "7"}


def test_policy_respects_method_attempt_and_retry_after():
    policy = ExponentialBackoffRetryPolicy(max_attempts=3)
    response = Response()

    assert policy.should_retry(method="GET", attempt=1, response=response)
    assert not policy.should_retry(method="POST", attempt=1, response=response)
    assert not policy.should_retry(method="GET", attempt=3, response=response)
    assert policy.delay_seconds(attempt=1, response=response) == 7


def test_policy_validates_configuration():
    try:
        ExponentialBackoffRetryPolicy(max_attempts=0)
    except ValueError as error:
        assert "max_attempts" in str(error)
    else:
        raise AssertionError("invalid max_attempts was accepted")


def test_package_metadata_and_entry_point():
    transport_entries = {
        entry.name: entry
        for entry in distribution("swarmauri_transport_retry").entry_points
        if entry.group == "swarmauri.transports"
    }
    assert transport_entries["RetryingHttpClient"].load() is RetryingHttpClient
