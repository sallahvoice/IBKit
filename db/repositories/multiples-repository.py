from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import date
from db.repositories.base_repository import BaseRepository
from db.connection import db


@dataclass(frozen=True, slots=True)
class MultiplesRepository(BaseRepository):
    """Repository for managing financial multiples data."""

    super().__init__("multiples")

    def create_multiples(self, multiples_data: Dict) -> int:
        """Insert financial multiples data"""
        query = f"""INSERT INTO {self.table_name} (ticker,
        name,
        forward_price_to_book,
        forward_pe,
        trailing_pe,
        forward_price_to_sale,
        trailing_ev_to_ebit,
        trailing_ev_to_sales
        )

        VALUES %(ticker)s,
        %(name)s,
        %(forward_price_to_book)s,
        %(forward_pe)s,
        %(trailing_pe)s,
        %(forward_price_to_sale)s,
        %(trailing_ev_to_ebit)s,

        ON DUPLICATE KEY UPDATE
        forward_price_to_book = VALUES(forward_price_to_book),
        forward_pe = VALUES(forward_pe),
        trailing_pe = VALUES(trailing_pe),
        forward_price_to_sale = VALUES(forward_price_to_sale),
        trailing_ev_to_ebit = VALUES(trailing_ev_to_ebit),
        trailing_ev_to_sales = VALUES(trailing_ev_to_sales)
        """
        
        with db.get_cursor() as cursor:
            cursor.excute(query, multiples_data)
            return cursor.lastrowid
    
    def get_multiples_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Retrieve financial multiples by ticker"""
        query = f"SELECT * FROM {self.table_name} WHERE ticker = %s"
        with db.get_cursor() as cursor:
            cursor.execute(query, (ticker,))
            return cursor.fetchone()
    
    def get_all_multiples(self) -> List[Dict]:
        """Retrieve all financial multiples"""
        query = f"SELECT * FROM {self.table_name}"
        with db.get_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()