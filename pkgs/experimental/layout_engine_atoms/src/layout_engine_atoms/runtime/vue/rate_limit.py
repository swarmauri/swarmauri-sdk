"""Simple in-memory rate limiting for events and WebSocket connections."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting.

    Args:
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds
        identifier_key: Function to extract identifier from request
            (e.g., IP address, user ID, session ID)
    """

    max_requests: int = 60
    window_seconds: int = 60

    def __post_init__(self) -> None:
        if self.max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")


class InMemoryRateLimiter:
    """Simple in-memory rate limiter using sliding window algorithm.

    Note:
        This is a basic implementation suitable for single-instance deployments.
        For distributed systems, consider using Redis-based rate limiting.

    Example:
        >>> limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
        >>> async def handler(request: Request):
        ...     await limiter.check_rate_limit(request)
        ...     # ... handle request
    """

    def __init__(
        self, max_requests: int = 60, window_seconds: int = 60, cleanup_interval: int = 300
    ) -> None:
        """Initialize the rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            cleanup_interval: Interval in seconds to clean up old entries
        """
        self.config = RateLimitConfig(
            max_requests=max_requests, window_seconds=window_seconds
        )
        self.cleanup_interval = cleanup_interval
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task[Any] | None = None

    def start_cleanup(self) -> None:
        """Start background cleanup task.

        Note: Only starts if called from within an async context with a running event loop.
        If called during initialization before the event loop starts, this will silently skip.
        """
        if self._cleanup_task is None:
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._cleanup_loop())
            except RuntimeError:
                # No event loop running yet - this is expected during app initialization
                # The cleanup task is optional and only helps with long-running memory efficiency
                pass

    async def stop_cleanup(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Periodically clean up old request records."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_old_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}", exc_info=True)

    async def _cleanup_old_entries(self) -> None:
        """Remove old request timestamps that are outside the window."""
        current_time = time.time()
        cutoff = current_time - self.config.window_seconds

        async with self._lock:
            # Remove completely empty entries
            empty_keys = [
                key for key, timestamps in self._requests.items() if not timestamps
            ]
            for key in empty_keys:
                del self._requests[key]

            # Clean old timestamps from each entry
            for timestamps in self._requests.values():
                while timestamps and timestamps[0] < cutoff:
                    timestamps.popleft()

    def _get_identifier(self, request: Request) -> str:
        """Extract identifier from request (e.g., IP address).

        Can be overridden to use different identifiers like user ID or session ID.
        """
        # Try to get real IP from X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Fall back to client IP
        if request.client:
            return request.client.host

        # Last resort
        return "unknown"

    async def check_rate_limit(
        self, request: Request, identifier: str | None = None
    ) -> None:
        """Check if request is within rate limit.

        Args:
            request: The FastAPI request
            identifier: Optional custom identifier (defaults to IP address)

        Raises:
            HTTPException: With status 429 if rate limit exceeded
        """
        identifier = identifier or self._get_identifier(request)
        current_time = time.time()
        cutoff = current_time - self.config.window_seconds

        async with self._lock:
            timestamps = self._requests[identifier]

            # Remove old timestamps
            while timestamps and timestamps[0] < cutoff:
                timestamps.popleft()

            # Check if limit exceeded
            if len(timestamps) >= self.config.max_requests:
                logger.warning(
                    f"Rate limit exceeded for {identifier}: "
                    f"{len(timestamps)} requests in {self.config.window_seconds}s"
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {self.config.max_requests} "
                    f"requests per {self.config.window_seconds} seconds.",
                    headers={"Retry-After": str(self.config.window_seconds)},
                )

            # Record this request
            timestamps.append(current_time)

    async def get_usage(self, identifier: str) -> dict[str, int]:
        """Get current usage stats for an identifier.

        Args:
            identifier: The identifier to check

        Returns:
            Dict with 'count' and 'remaining' keys
        """
        current_time = time.time()
        cutoff = current_time - self.config.window_seconds

        async with self._lock:
            timestamps = self._requests.get(identifier, deque())

            # Remove old timestamps
            while timestamps and timestamps[0] < cutoff:
                timestamps.popleft()

            count = len(timestamps)
            remaining = max(0, self.config.max_requests - count)

            return {
                "count": count,
                "remaining": remaining,
                "limit": self.config.max_requests,
                "window_seconds": self.config.window_seconds,
            }


class WebSocketRateLimiter:
    """Rate limiter specifically for WebSocket messages.

    Example:
        >>> limiter = WebSocketRateLimiter(max_messages=100, window_seconds=60)
        >>> await limiter.check_message_rate(websocket.client.host, "subscribe")
    """

    def __init__(
        self, max_messages: int = 100, window_seconds: int = 60
    ) -> None:
        """Initialize WebSocket rate limiter.

        Args:
            max_messages: Maximum messages per window
            window_seconds: Time window in seconds
        """
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._messages: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check_message_rate(
        self, client_identifier: str, action: str
    ) -> bool:
        """Check if client is within message rate limit.

        Args:
            client_identifier: Client identifier (e.g., IP address)
            action: The action type (e.g., 'subscribe', 'publish')

        Returns:
            True if within limit, False if exceeded
        """
        current_time = time.time()
        cutoff = current_time - self.window_seconds

        async with self._lock:
            timestamps = self._messages[client_identifier]

            # Remove old timestamps
            while timestamps and timestamps[0] < cutoff:
                timestamps.popleft()

            # Check if limit exceeded
            if len(timestamps) >= self.max_messages:
                logger.warning(
                    f"WebSocket message rate limit exceeded for {client_identifier}: "
                    f"{action} action"
                )
                return False

            # Record this message
            timestamps.append(current_time)
            return True
