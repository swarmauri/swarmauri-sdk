import pytest
from autoapi_client import AutoAPIClient
from unittest.mock import MagicMock


@pytest.mark.unit
def test_enter_returns_self():
    client = AutoAPIClient("http://example.com")
    with client as ctx:
        assert ctx is client


@pytest.mark.unit
def test_exit_closes_owned_client():
    client = AutoAPIClient("http://example.com")
    client._client.close = MagicMock()
    with client:
        pass
    client._client.close.assert_called_once_with()


@pytest.mark.unit
def test_close_does_not_close_unowned_client():
    mock = MagicMock()
    client = AutoAPIClient("http://example.com", client=mock)
    client.close()
    mock.close.assert_not_called()
