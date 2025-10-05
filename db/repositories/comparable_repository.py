from typing import Optional, Dict, List
from datetime import date
from db.repositories.base_repository import BaseRepository
from db.connection import db


class MultiplesRepository(BaseRepository):
    """Repository for managing comparable companies multiples."""

    def __init__(self):
        super().__init__("comparable_companies") 

    def create_comparable(self, comp_data: Dict) -> int:
        """Store a comparable company's multiples"""
        query = f"""
            INSERT INTO {self.table_name} (
                ticker,
                name,
                forward_price_to_book,
                forward_pe,
                trailing_pe,
                forward_price_to_sales,
                trailing_ev_to_ebit,
                trailing_ev_to_sales
            )
            VALUES (
                %(ticker)s,
                %(name)s,
                %(forward_price_to_book)s,
                %(forward_pe)s,
                %(trailing_pe)s,
                %(forward_price_to_sales)s,
                %(trailing_ev_to_ebit)s,
                %(trailing_ev_to_sales)s
            )
        """
        
        with db.get_cursor() as cursor:
            cursor.execute(query, comp_data)
            return cursor.lastrowid

    def get_comparables_for_set(self, set_id: int) -> List[Dict]:
        """Get all comparable companies for a set"""
        query = f"""
            SELECT c.* FROM {self.table_name} c
            JOIN comparable_set_members s ON c.ticker = s.company_ticker
            WHERE s.set_id = %s
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (set_id,))
            return cursor.fetchall()

    def get_comparable_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get comparable company by ticker"""
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE ticker = %s
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (ticker,))
            return cursor.fetchone()