from fastapi import APIRouter
from db.repositories.snapshot_repository import create_snapshot
from typing import Dict


router = APIRouter(prefix="/comparable")

router.get("/")
async def read_snapshot(snapshot_data: Dict):
    await create_snapshot(snapshot_data)