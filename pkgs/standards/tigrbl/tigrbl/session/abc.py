from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class SessionABC(ABC):
    """
    Authoritative Tigrbl session interface.

    All concrete sessions MUST be natively transactional and implement the
    methods below. This ABC is intentionally minimal and backend-agnostic.
    """

    # ---- Transactions ----
    @abstractmethod
    async def begin(self) -> None:
        """Open a native transaction for this session."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""

    @abstractmethod
    def in_transaction(self) -> bool:
        """Return True iff a transaction is currently open."""

    # ---- CRUD surface ----
    @abstractmethod
    async def get(self, model: type, ident: Any) -> Any | None:
        """Fetch one instance by primary key (model, ident)."""

    @abstractmethod
    def add(self, obj: Any) -> None:
        """Stage a new/dirty object for persistence."""

    @abstractmethod
    async def delete(self, obj: Any) -> None:
        """Stage an object for deletion."""

    @abstractmethod
    async def flush(self) -> None:
        """Flush staged changes to the underlying store (still in TX)."""

    @abstractmethod
    async def refresh(self, obj: Any) -> None:
        """Refresh the object from the store (respecting the current TX view)."""

    @abstractmethod
    async def execute(self, stmt: Any) -> Any:
        """
        Execute a backend-native statement.

        The result (if any) SHOULD provide a minimal facade compatible with:
          - .scalars().all()
          - .scalar_one()
        to ease integration with higher-level helpers.
        """

    # ---- Lifecycle / async marker ----
    @abstractmethod
    async def close(self) -> None:
        """Release underlying resources (connections, cursors, etc.)."""

    @abstractmethod
    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        """
        Execute a callback against the underlying native handle.

        Presence of this method also acts as the "async session" marker for code
        paths that need to distinguish sync-vs-async sessions.
        """
