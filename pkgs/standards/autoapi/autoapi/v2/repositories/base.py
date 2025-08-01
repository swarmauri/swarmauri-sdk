"""
Base Repository - Common data access patterns for AutoAPI.

Provides base functionality for repository implementations including
common CRUD operations and database session management.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, List, Optional, Type, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..jsonrpc_models import create_standardized_error

T = TypeVar("T")


class BaseRepository(ABC):
    """Base repository providing common data access patterns."""

    def __init__(self, db: Union[Session, AsyncSession], model_class: Type[T]):
        self.db = db
        self.model_class = model_class
        self._is_async = hasattr(db, "scalar")

    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by primary key."""
        if self._is_async:
            return await self.db.scalar(
                select(self.model_class).where(self.model_class.id == id)
            )
        else:
            return (
                self.db.query(self.model_class)
                .filter(self.model_class.id == id)
                .first()
            )

    async def exists(self, id: Any) -> bool:
        """Check if entity exists by primary key."""
        entity = await self.get_by_id(id)
        return entity is not None

    async def create(self, **kwargs) -> T:
        """Create new entity."""
        entity = self.model_class(**kwargs)
        self.db.add(entity)
        await self._flush()
        return entity

    async def update_by_id(self, id: Any, **kwargs) -> Optional[T]:
        """Update entity by primary key."""
        entity = await self.get_by_id(id)
        if entity is None:
            return None

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        await self._flush()
        return entity

    async def delete_by_id(self, id: Any) -> bool:
        """Delete entity by primary key."""
        entity = await self.get_by_id(id)
        if entity is None:
            return False

        await self.db.delete(entity)
        await self._flush()
        return True

    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """List all entities with optional pagination."""
        query = select(self.model_class).offset(offset)
        if limit:
            query = query.limit(limit)

        if self._is_async:
            result = await self.db.scalars(query)
            return list(result.all())
        else:
            return (
                self.db.query(self.model_class)
                .offset(offset)
                .limit(limit or 1000)
                .all()
            )

    async def count(self) -> int:
        """Count total entities."""
        if self._is_async:
            result = await self.db.scalar(select(func.count(self.model_class.id)))
            return result or 0
        else:
            return self.db.query(self.model_class).count()

    async def find_by(self, **filters) -> List[T]:
        """Find entities by arbitrary filters."""
        query = select(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.where(getattr(self.model_class, key) == value)

        if self._is_async:
            result = await self.db.scalars(query)
            return list(result.all())
        else:
            return self.db.query(self.model_class).filter_by(**filters).all()

    async def find_one_by(self, **filters) -> Optional[T]:
        """Find single entity by arbitrary filters."""
        results = await self.find_by(**filters)
        return results[0] if results else None

    async def _flush(self) -> None:
        """Flush changes to database."""
        try:
            if self._is_async and hasattr(self.db, "flush"):
                await self.db.flush()
            elif hasattr(self.db, "flush"):
                self.db.flush()
        except Exception as exc:
            await self._rollback()
            self._handle_db_error(exc)

    async def _rollback(self) -> None:
        """Rollback transaction."""
        if self._is_async and hasattr(self.db, "rollback"):
            await self.db.rollback()
        elif hasattr(self.db, "rollback"):
            self.db.rollback()

    def _handle_db_error(self, exc: Exception) -> None:
        """Handle database errors and convert to standardized HTTP errors."""
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        import re

        if isinstance(exc, IntegrityError):
            # Handle duplicate key violations
            raw = str(exc.orig) if hasattr(exc, "orig") else str(exc)
            if "already exists" in raw or "UNIQUE constraint" in raw:
                dup_re = re.compile(
                    r"Key \((?P<col>[^)]+)\)=\((?P<val>[^)]+)\) already exists", re.I
                )
                match = dup_re.search(raw)

                if match:
                    msg = (
                        f"Duplicate value '{match['val']}' for field '{match['col']}'."
                    )
                else:
                    msg = "Duplicate key value violates a unique constraint."

                http_exc, _, _ = create_standardized_error(
                    409, message=msg, rpc_code=-32099
                )
                raise http_exc from exc

            # Handle foreign key violations
            if "foreign key" in raw:
                http_exc, _, _ = create_standardized_error(422, rpc_code=-32097)
                raise http_exc from exc

        elif isinstance(exc, SQLAlchemyError):
            http_exc, _, _ = create_standardized_error(
                500, message=f"Database error: {exc}"
            )
            raise http_exc from exc

        # Re-raise other exceptions
        raise exc
