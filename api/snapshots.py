from fastapi import APIRouter
from db.repositories.snapshot_repository import SnapshotRepository
from typing import Dict

snapshot_repo = SnapshotRepository()

router = APIRouter(prefix="/comparable")

router.get("/")
def read_snapshot(snapshot_data: Dict, repo: SnapshotRepository = Depends(lambda: snapshot_repo)):
    return repo.create_snapshot(snapshot_data)