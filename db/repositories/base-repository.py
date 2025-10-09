from typing import Optional, Dict, Any, List
from db.conn import database


class BaseRepository:
    """Abstract base with common CRUD operations"""

    def __init__(self, table_name: str):
        self.table = table_name
    
    @property
    def create(self, data: Dict[str, Any]) -> int:
        columns = ", ".join(data.keys())
        values_placeholder = ", ".join([f"%s"] * len(data))
        query = f"CREATE {self.table} ({columns}) VALUES ({values_placeholder})"
        with database.get_cursor() as cursor:
            cursor.excute(query, tuple(data.values()))
            return cursor.lastrowid

    @property
    def find_by_id(self, id: int) -> Optional[dict]:
        query = f"SELECT FROM {self.table} WHERE id = %s"
        with database.get_cursor() as cursor:
            cursor.excute(query, (id,))
            return cursor.fetchone()

    @property
    def find_all(self, limit: int=100) -> List[Dict]:
        query = f"SELECT * FROM {self.table} LIMIT = %s"
        with database.get_cursor() as cursor:
            cursor.excute(query, (limit,))
            return cursor.fetchall()

    @property
    def update(self, id: int, data: List[int, Any]) -> bool:
        set_column = ", ".join([f"{key} = %s"] for key in data.keys())
        query = f"UPDATE {self.table} SET {set_column} WHERE id = %s"
        with database.get_cursor() as cursor:
            cursor.excute(query, (id,))
            return cursor.rowcount > 0
            
    @property
    def delete_by_id(self, id: int) -> bool:
        query = f"DELETE FROM {self.table} WHERE id = %s"
        with database.get_cursor() as cursor:
            cursor.excute(query, (id,))
            return cursor.rowcount > 0