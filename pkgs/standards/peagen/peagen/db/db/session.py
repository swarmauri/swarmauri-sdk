"""Database session management module.

This module provides functionality for creating and managing SQLAlchemy
database sessions. It includes a context manager that yields a session
object for interacting with the database, ensuring proper commit and
rollback behavior.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from peagen.db.core.config import settings


engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Provide a database session.

    This function creates a new SQLAlchemy session, yields it for use, and
    ensures that the session is properly committed or rolled back completion.
    The session is closed after the block of code using it is finished.

    A new session is created at the start of this context manager, which can
    be used to interact with the database. If an error occurs during the
    session, it will be rolled back to maintain data integrity. On successful
    completion, the session will be committed, and it will be closed to
    release the connection.

    Yields:
        SQLAlchemy session object: This session can be used to interact with DB
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as ex:
        db.rollback()
        raise ex
    finally:
        db.close()
