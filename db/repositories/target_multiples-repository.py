from typing import Optional, Dict, List
from datetime import date
from db.repositories.base_repository import BaseRepository
from db.connection import db


class TargetMultiplesRepository(BaseRepository):
    def __init__(self):
        super().__init__("valuation_multiples")
    
    def create_multiples(self, multiples_data: Dict) -> int:
        """Store calculated multiples for target company"""
        query = f"""
            INSERT INTO {self.table_name} (
                company_id,
                calculation_date,
                forward_pe,
                trailing_pe,
                forward_price_to_book,
                forward_price_to_sales,
                forward_ev_to_ebit,
                forward_ev_to_sales,
                trailing_ev_to_ebit,
                trailing_ev_to_sales,
                model_version
            )
            VALUES (
                %(company_id)s,
                %(calculation_date)s,
                %(forward_pe)s,
                %(trailing_pe)s,
                %(forward_price_to_book)s,
                %(forward_price_to_sales)s,
                %(forward_ev_to_ebit)s,
                %(forward_ev_to_sales)s,
                %(trailing_ev_to_ebit)s,
                %(trailing_ev_to_sales)s,
                %(model_version)s
            )
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, multiples_data)
            return cursor.lastrowid

        with db.get_cursor() as cursor:
            cursor.execute(query, multiples_data)
            return cursor.lastrowid
    
    def get_latest_multiples(self, company_id: int) -> Optional[Dict]:
        """Get most recent multiples for a company"""
        query = f"""
        SELECT * FROM {self.table_name}
        WHERE id = %s
        ORDER BY calculation_date DESC
        LIMIT 1
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (company_id,))
            return cursor.fetchone()
    
    def get_multiples_by_date(self, company_id: int, calc_date: date) -> Optional[Dict]:

        """Get multiples for specific date"""
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE company_id = %s AND calculation_date = %s
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (company_id, calc_date))
            return cursor.fetchone()
