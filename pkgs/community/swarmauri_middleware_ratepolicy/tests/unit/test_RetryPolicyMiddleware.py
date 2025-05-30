import pytest
from swarmauri_middleware_ratepolicy.RetryPolicyMiddleware import RetryPolicyMiddleware


@pytest.mark.unit
class TestRetryPolicyMiddleware:
    """Unit tests for the RetryPolicyMiddleware class."""

    def test_init(self):
        """Test initialization of RetryPolicyMiddleware with parameters."""
        max_retries = 5
        initial_wait = 2.5

        middleware = RetryPolicyMiddleware(
            max_retries=max_retries, initial_wait=initial_wait
        )

        assert middleware.max_retries == max_retries
        assert middleware.initial_wait == initial_wait

    @pytest.mark.parametrize(
        "max_retries,initial_wait",
        [
            (0, 1),
            (10, 5),
            (-1, 1),  # Should be clamped to 0
            (5, -1),  # Should be clamped to 0
        ],
    )
    def test_init_edge_cases(self, max_retries, initial_wait):
        """Test edge cases for initialization parameters."""
        middleware = RetryPolicyMiddleware(
            max_retries=max_retries, initial_wait=initial_wait
        )

        # Ensure max_retries can't be negative
        assert middleware.max_retries == max(0, max_retries)
        # Ensure initial_wait can't be negative
        assert middleware.initial_wait == max(0, initial_wait)

    @pytest.mark.parametrize("max_retries,expected_retries", [(3, 3), (5, 5), (0, 0)])
    def test_dispatch_retries(self, max_retries, expected_retries, mocker):
        """Test that dispatch method respects max_retries."""
        # Setup
        middleware = RetryPolicyMiddleware(max_retries=max_retries)
        request = mocker.MagicMock()
        call_next = mocker.MagicMock(side_effect=Exception("Simulated failure"))

        # Test
        with pytest.raises(Exception):
            middleware(request, call_next)

        # Verify the number of attempts
        assert call_next.call_count == expected_retries + 1  # +1 for initial attempt

    def test_dispatch_success(self, mocker):
        """Test successful dispatch without any retries."""
        # Setup
        middleware = RetryPolicyMiddleware(max_retries=3)
        request = mocker.MagicMock()
        call_next = mocker.MagicMock(return_value="Success Response")

        # Test
        response = middleware(request, call_next)

        # Verify
        assert response == "Success Response"
        assert call_next.call_count == 1

    def test_call_magic_method(self, mocker):
        """Test that __call__ method calls dispatch."""
        # Setup
        middleware = RetryPolicyMiddleware(max_retries=3)
        request = mocker.MagicMock()
        call_next = mocker.MagicMock(return_value="Success Response")
        dispatch_mock = mocker.patch.object(
            middleware, "dispatch", return_value="Dispatch Response"
        )

        # Test
        response = middleware(request, call_next)

        # Verify
        assert response == "Dispatch Response"
        dispatch_mock.assert_called_once_with(request, call_next)

    def test_class_attributes(self):
        """Test that class attributes are correctly set."""
        middleware = RetryPolicyMiddleware()
        assert middleware.resource == "Middleware"
        assert middleware.type == "RetryPolicyMiddleware"
