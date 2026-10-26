"""Database helper and session initialization."""

import logging
from sqlalchemy import text
from app.core.database import engine, Base
import app.models  # ensure all models are registered

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize database tables and create them if not exist."""
    try:
        async with engine.begin() as conn:
            # Create all tables if using SQLite or clean DB
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to database on startup: {e}")
