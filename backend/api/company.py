from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.repositories.company_repository import CompanyRepository

company_repo = CompanyRepository()

router = APIRouter(prefix="/company")


class CompanyCreate(BaseModel):
    ticker: str
    name: str = None
    incorporation: str = None
    sector: str = None
    market_cap: float = None


@router.post("/")
def create_company(
    company: CompanyCreate, repo: CompanyRepository = Depends(lambda: company_repo)
):
    """Create or update a company"""
    try:
        company_id = repo.create_company(company.dict())
        return {"id": company_id, "message": "Company created/updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{ticker}")
def get_company_by_ticker(
    ticker: str, repo: CompanyRepository = Depends(lambda: company_repo)
):
    """Get company by ticker"""
    company = repo.get_company_by_ticker(ticker)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/sector/{sector}")
def get_company_by_sector(
    sector: str, repo: CompanyRepository = Depends(lambda: company_repo)
):
    """Get all companies in a sector"""
    companies = repo.get_company_by_sector(sector)
    return {"sector": sector, "companies": companies}
