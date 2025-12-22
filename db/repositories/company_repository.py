from typing import Optional, Dict, List
from db.repositories.base_repository import BaseRepository
from db.database import database
from backend.domain.company import Company


class CompanyRepository(BaseRepository):
    """Repository for managing company records in the database"""

    def __init__(self):
        super().__init__("companies")
    
    def create_company(self, company_data: Dict) -> int:
        """Create or update a company record in the database"""
        
        company_ticker = Company.normalize_ticker(company_data.get("ticker"))
        if not Company.is_valid_ticker(company_ticker):
            raise ValueError("Invalid ticker format")
        
        # Update the dict with normalized ticker
        company_data["ticker"] = company_ticker
        company = Company.create_company_from_dict(company_data)
        
        query = f"""
            INSERT INTO {self.table} (ticker, name, incorporation, sector, market_cap)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            incorporation = VALUES(incorporation),
            sector = VALUES(sector),
            market_cap = VALUES(market_cap)
        """
        
        values = (
            company.ticker,
            company.name,
            company.incorporation,
            company.sector,
            company.market_cap,
        )
        
        with database.get_cursor() as cursor:
            cursor.execute(query, values)  
            return cursor.lastrowid

    def get_company_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Fetch a company record by its ticker symbol"""
        normalized_ticker = Company.normalize_ticker(ticker)
        query = "SELECT * FROM companies WHERE ticker = %s"
        with database.get_cursor() as cursor:
            cursor.execute(query, (normalized_ticker,))  
            return cursor.fetchone()
        
    def get_company_by_sector(self, sector: str) -> List[Dict]:
        """Fetch all companies by sector"""
        query = "SELECT * FROM companies WHERE sector = %s"
        with database.get_cursor() as cursor:
            cursor.execute(query, (sector,))
            return cursor.fetchall()
    
    def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """Fetch a company record by its ID"""
        query = "SELECT * FROM companies WHERE id = %s"
        with database.get_cursor() as cursor:
            cursor.execute(query, (company_id,))
            return cursor.fetchone()