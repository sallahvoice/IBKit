"""Loads environment variables and configures database connection pooling.

Provides a DatabaseConnection instance for use throughout the application.
"""

import os

from dotenv import load_dotenv
from mysql.connector import Error, pooling

from backend.utils.logger import get_logger

from .conn import DatabaseConnection

logger = get_logger(__file__)
load_dotenv()


def create_db_pool():
    """Create and return a MySQL connection pool."""
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="main_pool",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        return pool
    except Error as e:
        logger.error("Error creating DB pool: %s", e)
        raise


def get_database():
    """Return a DatabaseConnection instance using the connection pool."""
    pool = create_db_pool()
    return DatabaseConnection(pool)


# Singleton instance for convenience
database = get_database()
