from fastapi import APIRouter, Depends
from db.repositories.company_repository import CompanyRepository

company_repo = CompanyRepository()

router = APIRouter(prefix="/company")

router.get("/")
def read_company(ticker: str, repo: CompanyRepository = Depends(lambda: company_repo)):
    return repo.create_company(ticker)