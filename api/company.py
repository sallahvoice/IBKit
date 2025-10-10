from fastapi import APIRouter, Depends
from db.repositories.company_repository import create_company


router = APIRouter(prefix="/company")

router.get("/")
async def read_company(ticker: str):
    await create_company(ticker)