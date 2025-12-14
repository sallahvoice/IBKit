from dataclasses import dataclass
from typing import Optional, Dict
from datetime import date
from db.repositories.base_repository import BaseRepository
from db.database import database


class SnapshotRepository(BaseRepository):

    def __init__(self):
        super().__init__("financial_snapshots")

    def create_snapshot(self, snapshot_data: Dict) -> int:
        """Insert financial snapshot"""
        query = f"""
        INSERT INTO {self.table_name} (company_id,
        snapshot_date,
        marginal_tax_rate,
        last_annual_revenue,
        last_annual_ebit,
        last_annual_net_income,
        last_annual_interest_expense,
        last_annual_tax_paid,
        trailing_sales,
        trailing_ebit,

        last_annual_debt,
        last_annual_cash,
        last_annual_equity,

        last_annual_capex,
        last_annual_chng_wc,
        last_annual_da,

        
        market_cap,
        current_shares_outstanding,
        current_beta

        ) 

        VALUES %(company_id)s,
        %(snapshot_date)s,

        %(marginal_tax_rate)s,

        %(last_annual_revenue)s,
        %(last_annual_ebit)s,
        %(last_annual_net_income)s,
        %(last_annual_interest_expense)s,
        %(last_annual_tax_paid)s,
        %(trailing_sales)s,
        %(trailing_ebit)s,

        %(last_annual_debt)s,
        %(last_annual_cash)s,
        %(last_annual_equity)s,

        %(last_annual_capex)s,
        %(last_annual_chng_wc)s,
        %(last_annual_da)s,

        %(market_cap)s,
        %(current_shares_outstanding)s,
        %(current_beta)s,
        ) 

        ON DUPLICATE KEY UPDATE
        last_annual_revenue = VALUES(last_annual_revenue),
        last_annual_ebit = VALUES(last_annual_ebit),
        last_annual_net_income = VALUES(last_annual_net_income),
        last_annual_interest_expense = VALUES(last_annual_interest_expense),
        last_annual_tax_paid = VALUES(last_annual_tax_paid),
        trailing_sales = VALUES(trailing_sales),
        trailing_ebit = VALUES(trailing_ebit),

        last_annual_debt = VALUES(last_annual_debt),
        last_annual_cash = VALUES(last_annual_cash),
        last_annual_equity = VALUES(last_annual_equity),

        last_annual_capex = VALUES(last_annual_capex),
        last_annual_chng_wc = VALUES(last_annual_chng_wc),
        last_annual_da = VALUES(last_annual_da),

        market_cap = VALUES(market_cap),
        current_shares_outstanding = VALUES(current_shares_outstanding),
        current_beta = VALUES(current_beta),
        """

        with database.get_cursor() as cursor:
            cursor.execute(query, (snapshot_data))
            return cursor.lastrowid


    def get_latest_snapshot(self, company_id: int) -> Optional[Dict]:
        """Get most recent snapshot for a company"""
        query = """
        SELECT * FROM financial_snapshots
        WHERE company_id = %s
        ORDER BY snapshot_date DESC
        LIMIT 1
        """

        with database.get_cursor() as cursor:
            cursor.execute(query, (company_id,))
            return cursor.fetchone()
 


    def get_snapshot_by_date(self, company_id: int, snapshot_date: date) -> Optional[Dict]:
        """Get specific snapshot"""
        query = """
        SELECT * FROM financial_snapshots
        WHERE company_id = %s AND snapshot_date = %s
        """

        with database.get_cursor() as cursor:
            cursor.execute(query, (company_id, snapshot_date))
            return cursor.fetchone()