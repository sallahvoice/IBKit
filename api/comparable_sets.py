from fastapi import APIRouter
from db.repositories.comparable_repository import create_comparable
from typing import Dict


router = APIRouter(prefix="/comparable")

router.get("/")
async def read_comparable(comp_data: Dict):
    await create_comparable(comp_data)