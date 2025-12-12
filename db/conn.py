import time
from backend.utils.logger import get_logger
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error


logger = get_logger(__file__)


class DatabaseConnection:

    def __init__(self, pool):
        self.pool = pool

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            logger.info(f"Database error : {e}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()
            
    @contextmanager
    def get_cursor_with_logging(self, dictionary=True):
        """Context manager with slow query logging"""
        start = time.time()
        with self.get_cursor(dictionary) as cursor:
            yield cursor
        duration = time.time() - start
        if duration > 0.1:
            logger.info(f"query too slow, took {duration:.2f}s")