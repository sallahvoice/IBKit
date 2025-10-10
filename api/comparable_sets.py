from fastapi import APIRouter
from db.repositories.comparable_repository import create_comparable
from typing import Dict


router = APIRouter(prefix="/comparable")

router.get("/")
def read_comparable(comp_data: Dict):
    create_comparable(comp_data)