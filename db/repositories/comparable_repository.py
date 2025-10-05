from typing import Optional, Dict, List
from datetime import date
from db.repositories.base_repository import BaseRepository
from db.connection import db


class MultiplesRepository(BaseRepository):
    """Repository for managing financial multiples data."""

    def __init__(self):
        super().__init__("comparable_companies") 

    def create_multiples(self, multiples_data: Dict) -> int:
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
                trailing_ev_to_sales,
                forward_ev_to_ebit,
                forward_ev_to_sales,
            )
            VALUES (
                %(ticker)s,
                %(forward_price_to_book)s,
                %(forward_pe)s,
                %(trailing_pe)s,
                %(forward_price_to_sales)s,
                %(trailing_ev_to_ebit)s,
                %(trailing_ev_to_sales)s,
                %(forward_ev_to_ebit)s,
                %(forward_ev_to_sales)s,
            )
        """
        
        with db.get_cursor() as cursor:
            cursor.execute(query, multiples_data)
            return cursor.lastrowid


    def get_comparables_for_set(self, set_id : int) -> List[Dict]:
        """Get all comparable companies for a comparable set"""
        query = f"""
            SELECT c.* FROM {self.table_name} c
            JOIN comparable_set_companies s ON c.ticker = s.company_ticker
            WHERE s.set_id = %s
            ORDER BY c.ticker
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (set_id,))
            return cursor.fetchall()


    def get_multiples_by_ticker(self, ticker: int) -> List[Dict]:
        """Get all multiples for a company"""
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE company_id = %s
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (ticker,))
            return cursor.fetchall()