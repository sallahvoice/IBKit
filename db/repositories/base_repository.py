"""repository file that defines a base class with crud methods that is inherited in other files classes"""

from db.database import database


class BaseRepository:
    """class with common CRUD operations"""

    def __init__(self, table_name: str):
        self.table = table_name

    def create(self, data):
        if not data:
            raise ValueError("No data provided")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"

        with database.get_cursor() as cursor:
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def find_by_id(self, id):
        query = f"SELECT * FROM {self.table} WHERE id = %s"

        with database.get_cursor() as cursor:
            cursor.execute(query, (id,))
            return cursor.fetchone()

    def find_all(self, limit=100):
        query = f"SELECT * FROM {self.table} LIMIT %s"

        with database.get_cursor() as cursor:
            cursor.execute(query, (limit,))
            return cursor.fetchall()

    def update(self, id, data):
        set_clause = ", ".join(f"{k} = %s" for k in data)
        query = f"UPDATE {self.table} SET {set_clause} WHERE id = %s"

        with database.get_cursor() as cursor:
            cursor.execute(query, tuple(data.values()) + (id,))
            return cursor.rowcount > 0

    def delete_by_id(self, id):
        query = f"DELETE FROM {self.table} WHERE id = %s"

        with database.get_cursor() as cursor:
            cursor.execute(query, (id,))
            return cursor.rowcount > 0
