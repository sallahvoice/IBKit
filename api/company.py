from fastapi import APIRouter, Depends
from db.repositories.company_repository import create_company


router = APIRouter(prefix="/company")

router.get("/")
def read_company(ticker: str):
    create_company(ticker)