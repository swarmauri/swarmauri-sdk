"""Entry point for the backend app."""

import logging
from fastapi import FastAPI

from peagen.db.session import engine
from peagen.orm.models import Base
from peagen.db.api.v1.main import ROUTES


# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

@app.get("/health")
def health_check():
    """
    Health check endpoint.

    This endpoint is used to check the health status of the core application.

    Returns:
        dict: A dictionary containing the health status of the core application.
    """
    return {"status": "core healthy"}


# Include API routers
app_v1_router = ROUTES
app.include_router(app_v1_router)

# Create all tables if they do not exist
Base.metadata.create_all(bind=engine)  # type: ignore


@app.on_event("startup")
def startup():
    """Startup event handler."""
    logger.info("Starting up the application.")

    # Check the database connection
    try:
        with engine.connect() as connection:
            logger.info(
                "Database connection established successfully." + str(connection)
            )
    except Exception as ex:
        logger.error(f"Database connection failed: {ex}")
        raise


@app.on_event("shutdown")
def shutdown():
    """Shutdown event handler."""
    logger.info("Shutting down the application.")
