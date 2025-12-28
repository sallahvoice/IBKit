"""Module for managing database resources (connections and cursors)."""

import time
from contextlib import contextmanager

from mysql.connector import Error

from backend.utils.logger import get_logger

logger = get_logger(__file__)


class DatabaseConnection:
    """Provides context managers for connections and cursors.

    Ensures that connections and cursors are opened and closed properly
    and supports optional slow query logging.
    """

    def __init__(self, pool):
        """Initialize with a MySQLConnectionPool instance."""
        self.pool = pool

    @contextmanager
    def get_connection(self):
        """Context manager for database connections.

        Commits on success, rolls back on error, and closes connection.
        """
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            logger.error("Database error: %s", e)
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager for database cursors.

        Args:
            dictionary (bool): If True, cursor returns rows as dicts.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()

    @contextmanager
    def get_cursor_with_logging(self, dictionary=True):
        """Context manager for cursors with slow query logging."""
        start = time.time()
        with self.get_cursor(dictionary) as cursor:
            yield cursor
        duration = time.time() - start
        if duration > 0.1:
            logger.info("Query too slow, took %.2f seconds", duration)
