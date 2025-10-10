from fastapi import APIRouter
from db.repositories.comparable_repository import CompanyRepository
from typing import Dict

comparable_repo = CompanyRepository()

router = APIRouter(prefix="/comparable")

router.get("/")
def read_comparable(comp_data: Dict, repo: CompanyRepository = Depends(lambda: comparable_repo)):
    return repo.create_comparable(comp_data)